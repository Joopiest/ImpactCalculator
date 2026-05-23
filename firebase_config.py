import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import streamlit as st

# Initialize Firebase Admin SDK
try:
    # Check if firebase is already initialized to prevent duplicate app creation errors
    if not firebase_admin._apps:
        # 1. Try to load from Streamlit Secrets (for cloud deployment)
        secrets_loaded = False
        try:
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                secrets_loaded = True
        except Exception:
            pass
            
        # 2. Try to load from local JSON file
        if not secrets_loaded:
            cred_path = "joopiest-f16cf-firebase-adminsdk-fbsvc-3547a4eba1.json"
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Fallback using the absolute directory of this script file
                current_dir = os.path.dirname(os.path.abspath(__file__))
                fallback_path = os.path.join(current_dir, cred_path)
                if os.path.exists(fallback_path):
                    cred = credentials.Certificate(fallback_path)
                    firebase_admin.initialize_app(cred)
                else:
                    deploy_path = os.path.join(current_dir, "NAPAT_github_deploy", cred_path)
                    if os.path.exists(deploy_path):
                        cred = credentials.Certificate(deploy_path)
                        firebase_admin.initialize_app(cred)
                    else:
                        raise FileNotFoundError("Firebase credentials JSON file not found locally and no Streamlit Secrets configured.")
except Exception as e:
    print(f"Error initializing Firebase Admin: {e}")

# Get Firestore instance
try:
    db = firestore.client()
except Exception as e:
    db = None
    print(f"Error connecting to Firestore: {e}")

def is_db_connected():
    return db is not None

def save_draft(employee_id, project_id, draft_data):
    """
    Saves or updates a evaluation draft in Firestore
    """
    if not db:
        return False
    try:
        doc_id = f"draft_{employee_id}_{project_id}"
        doc_ref = db.collection("drafts").document(doc_id)
        doc_ref.set({
            "employee_id": employee_id,
            "project_id": project_id,
            "project_name": draft_data.get("project_name", ""),
            "organization": draft_data.get("organization", ""),
            "report_type": draft_data.get("report_type", ""),
            "meta_krrn": draft_data.get("meta_krrn", ""),
            "meta_krid": draft_data.get("meta_krid", ""),
            "meta_krrn_related": draft_data.get("meta_krrn_related", ""),
            "meta_patent_id": draft_data.get("meta_patent_id", ""),
            "chk_b5_text": draft_data.get("chk_b5_text", ""),
            "sections": draft_data.get("sections", {}),
            "fields": draft_data.get("fields", {}),
            "saved_at": firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"Firestore save_draft error: {e}")
        return False

def load_drafts(employee_id):
    """
    Loads all drafts saved for a specific employee ID
    """
    if not db:
        return []
    try:
        docs = db.collection("drafts").where("employee_id", "==", employee_id).stream()
        drafts = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            if "saved_at" in d and d["saved_at"]:
                # Convert firestore datetime to formatted string
                try:
                    dt = d["saved_at"]
                    if hasattr(dt, "to_datetime"): dt = dt.to_datetime()
                    d["saved_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    d["saved_at"] = str(d["saved_at"])
            else:
                d["saved_at"] = "-"
            drafts.append(d)
        return drafts
    except Exception as e:
        print(f"Firestore load_drafts error: {e}")
        return []

def load_user_evaluations(employee_id):
    """
    Loads all submitted evaluations for a specific employee ID
    """
    if not db:
        return []
    try:
        docs = db.collection("evaluations").where("employee_id", "==", employee_id).order_by("submitted_at", direction=firestore.Query.DESCENDING).stream()
        evals = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            if "submitted_at" in d and d["submitted_at"]:
                try:
                    dt = d["submitted_at"]
                    if hasattr(dt, "to_datetime"): dt = dt.to_datetime()
                    d["submitted_at_str"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    d["submitted_at_str"] = str(d["submitted_at"])
            else:
                d["submitted_at_str"] = "-"
            evals.append(d)
        return evals
    except Exception as e:
        print(f"Firestore load_user_evaluations error: {e}")
        # Fallback to unsorted if index missing
        try:
            docs = db.collection("evaluations").where("employee_id", "==", employee_id).stream()
            evals = []
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                evals.append(d)
            return evals
        except Exception as inner_e:
            print(f"Firestore load_user_evaluations fallback error: {inner_e}")
            return []

def delete_draft(draft_id):
    """
    Deletes a specific draft by its Firestore document ID
    """
    if not db:
        return False
    try:
        db.collection("drafts").document(draft_id).delete()
        return True
    except Exception as e:
        print(f"Firestore delete_draft error: {e}")
        return False

def submit_evaluation(evaluation_data):
    """
    Submits a completed evaluation report to Firestore and clears any draft
    """
    if not db:
        return False
    try:
        # Save assessment report
        doc_ref = db.collection("evaluations").document()
        evaluation_data["submitted_at"] = firestore.SERVER_TIMESTAMP
        doc_ref.set(evaluation_data)
        
        # Clean up existing draft if any
        emp_id = evaluation_data.get("employee_id")
        proj_id = evaluation_data.get("project_id")
        if emp_id and proj_id:
            draft_id = f"draft_{emp_id}_{proj_id}"
            db.collection("drafts").document(draft_id).delete()
            
        return True
    except Exception as e:
        print(f"Firestore submit_evaluation error: {e}")
        return False

def get_dashboard_stats():
    """
    Fetches raw data from Firestore to construct dashboard aggregates.
    Includes a fallback if sorting fails (e.g. missing indexes).
    """
    if not db:
        return None
    try:
        # Attempt sorted query first
        try:
            docs = db.collection("evaluations").order_by("submitted_at", direction=firestore.Query.DESCENDING).stream()
            docs_list = list(docs)
        except Exception as query_error:
            print(f"Firestore sorted query failed, falling back to unsorted: {query_error}")
            # Fallback: get all and sort in Python
            docs = db.collection("evaluations").stream()
            docs_list = list(docs)
            # Sort by submitted_at if it exists
            docs_list.sort(key=lambda x: x.to_dict().get("submitted_at") or datetime.min, reverse=True)

        evals = []
        total = 0
        organizations = {}
        
        for doc in docs_list:
            d = doc.to_dict()
            d["id"] = doc.id
            
            # Format datetime
            if "submitted_at" in d and d["submitted_at"]:
                try:
                    # Handle both datetime and Timestamp objects
                    dt = d["submitted_at"]
                    if hasattr(dt, "to_datetime"): # Firestore Timestamp
                        dt = dt.to_datetime()
                    
                    d["submitted_at_str"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    d["submitted_date"] = dt.date()
                except Exception:
                    d["submitted_at_str"] = str(d["submitted_at"])
                    d["submitted_date"] = datetime.now().date()
            else:
                d["submitted_at_str"] = "-"
                d["submitted_date"] = datetime.now().date()
                
            evals.append(d)
            total += 1
            
            # Group by organization
            org = d.get("organization", "Guest")
            organizations[org] = organizations.get(org, 0) + 1
            
        return {
            "total": total,
            "organizations": organizations,
            "evaluations": evals
        }
    except Exception as e:
        print(f"Firestore get_dashboard_stats critical error: {e}")
        return None

def check_project_submitted(project_id):
    """
    Checks if a project ID has already been submitted in evaluations
    Returns the document data dict if found, or None
    """
    if not db or not project_id:
        return None
    try:
        project_id = str(project_id).strip().upper()
        docs = db.collection("evaluations").where("project_id", "==", project_id).limit(1).stream()
        for doc in docs:
            d = doc.to_dict()
            if "submitted_at" in d and d["submitted_at"]:
                try:
                    dt = d["submitted_at"]
                    if hasattr(dt, "to_datetime"):
                        dt = dt.to_datetime()
                    d["submitted_at_str"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    d["submitted_at_str"] = str(d["submitted_at"])
            else:
                d["submitted_at_str"] = "-"
            return d
        return None
    except Exception as e:
        print(f"Firestore check_project_submitted error: {e}")
        return None

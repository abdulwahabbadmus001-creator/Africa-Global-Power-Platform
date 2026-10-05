export type Role = 'reader'|'researcher'|'contributor'|'reviewer'|'editor'|'senior_editor'|'managing_editor'|'super_admin'
export type PublicationStatus = 'draft'|'submitted'|'desk_review'|'editorial_review'|'revision_requested'|'source_check'|'approved'|'scheduled'|'published'|'rejected'
export type SubmissionMethod = 'form'|'upload'|'both'

export interface User {
  id: string; email?: string; first_name: string; last_name: string; role: Role;
  institution?: string|null; country?: string|null; expertise?: string|null; bio?: string|null;
  orcid?: string|null; website?: string|null; github?: string|null; collaboration_open: boolean;
  is_active?: boolean; is_email_verified?: boolean; email_verified_at?: string|null; created_at: string;
}

export interface Publication {
  id: string; author_id: string; assigned_editor_id?: string|null; title: string; slug: string;
  abstract: string; body: string; publication_type: string; submission_method: SubmissionMethod; topic: string; region?: string|null;
  country?: string|null; keywords: string[]; references: Array<{title?:string;url?:string;doi?:string}>;
  methodology?: string|null; limitations?: string|null; policy_implications?: string|null;
  status: PublicationStatus; current_version: number; scheduled_for?: string|null; published_at?: string|null;
  created_at: string; updated_at: string; author?: User|null;
}

export interface EditorialQueueItem {
  id:string; assigned_editor_id?:string|null; title:string; publication_type:string; submission_method:SubmissionMethod;
  topic:string; region?:string|null; country?:string|null; status:PublicationStatus; current_version:number;
  created_at:string; updated_at:string; author?:User|null;
}

export interface ManuscriptFile {
  id:string; publication_id:string; version_number:number; original_filename:string; mime_type:string; size_bytes:number;
  sha256:string; is_original_submission:boolean; public_on_publish:boolean; uploaded_at:string;
}

export interface TrustSnapshot {
  id:string; submission_id:string; publication_id:string; manuscript_file_id?:string|null; submission_sequence:number;
  publication_version:number; fingerprint_sha256:string; immutable:boolean; submitted_at:string;
}

export interface EditorTrustState {
  assigned_to_me:boolean; confidentiality_accepted:boolean; conflict_decision?:string|null; can_access_manuscript:boolean;
}

export interface TrustOverview {
  publication_id:string; files:ManuscriptFile[]; snapshots:TrustSnapshot[]; latest_snapshot?:TrustSnapshot|null;
  editor_state?:EditorTrustState|null;
}

export interface TrustAccessEvent {
  id:string; actor_name:string; actor_role?:string|null; action:string; object_type?:string|null; details:Record<string,unknown>;
  event_hash:string; created_at:string;
}

export interface Message { id:string; sender_id:string; recipient_id:string; subject:string; body:string; is_read:boolean; created_at:string; sender?:User; recipient?:User; context_type?:string|null; context_id?:string|null }
export interface Analytics { publication_id:string; views:number; unique_readers:number; saves:number; shares:number; downloads:number; source_clicks:number }

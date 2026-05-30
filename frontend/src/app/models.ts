// Domain types matching your FastAPI schemas

export interface User {
  id: number;
  name: string;
  email: string;
  year_in_school: string;
  major: string;
  university: string;
  created_at: string;
}

export interface Profile {
  user_id: number;
  tech_interests: string[];
  blind_spots: string[];
  experience_level: string;
  roadmap_stage: number;
  profile_complete: boolean;
}

export interface RoadmapAction {
  stage: number;
  title: string;
  description: string;
  action_type: string;
  completed: boolean;
}

export interface Opportunity {
  id: number;
  title: string;
  company: string;
  type: string;
  eligibility: string;
  is_paid: boolean;
  deadline: string | null;
  application_url: string;
}

export interface SavedOpportunity {
  id: number;
  opportunity_id: number;
  saved_at: string;
  deadline_reminder: boolean;
}

export interface Resume {
  id: number;
  file_url: string;
  ats_score: number | null;
  ai_feedback: string | null;
  uploaded_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
  is_active: boolean
  is_approved: boolean
  school_name: string
  created_at: string
}

export interface PaginatedResponse {
  users: User[]
  total: number
  pages: number
  current_page: number
  has_next: boolean
  has_prev: boolean
}

export interface CreateUserRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  school_name: string
  is_admin?: boolean
}

export interface UpdateUserRequest {
  email?: string
  first_name?: string
  last_name?: string
  password?: string
  school_name?: string
  is_admin?: boolean
  is_active?: boolean
  is_approved?: boolean
}

export interface ApprovalResponse {
  message: string
  approval: {
    id: number
    created_at: string
    is_approved: boolean
    admin_id: number
  }
}

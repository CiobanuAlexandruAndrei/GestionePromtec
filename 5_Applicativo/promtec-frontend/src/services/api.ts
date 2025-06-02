import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// If VITE_BACKEND_URL is empty or set to '/api', we use just '/api'
// Otherwise we append '/api' to the URL
const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
const baseURL = backendUrl === '/api' ? '/api' : `${backendUrl}/api`

const axiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  // not using session cookies
  withCredentials: false
})


// Setup axios interceptor for authentication
axiosInstance.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

export const API_URL = axiosInstance.defaults.baseURL

export const login = async (email: string, password: string) => {
  try {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await axiosInstance.post('/security/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    return response.data
  } catch (error) {
    console.error('Login request failed:', error)
    throw error
  }
}

interface User {
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

interface PaginatedResponse {
  users: User[]
  total: number
  pages: number
  current_page: number
  has_next: boolean
  has_prev: boolean
}

interface CreateUserRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  school_name: string
  is_admin?: boolean
}

interface UpdateUserRequest {
  email?: string
  first_name?: string
  last_name?: string
  password?: string
  school_name?: string
  is_admin?: boolean
  is_active?: boolean
  is_approved?: boolean
}

interface ApprovalResponse {
  message: string
  approval: {
    id: number
    created_at: string
    is_approved: boolean
    admin_id: number
  }
}

// Get all users (admin only)
export const getAllUsers = async (): Promise<User[]> => {
  try {
    const response = await axiosInstance.get('/user-management/users')
    return response.data.users
  } catch (error) {
    console.error('Failed to fetch all users:', error)
    throw error
  }
}

// Get approved users with pagination
export const getApprovedUsers = async (
  page: number = 1, 
  perPage: number = 10,
  sortBy?: string,
  sortOrder?: 'asc' | 'desc',
  search?: string,
  filters?: {
    school_name?: string;
    is_admin?: boolean;
    is_active?: boolean;
  }
): Promise<PaginatedResponse> => {
  try {
    const response = await axiosInstance.get('/user-management/users/approved', {
      params: {
        page,
        per_page: perPage,
        sort_by: sortBy,
        sort_order: sortOrder,
        search,
        ...filters
      }
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch approved users:', error)
    throw error
  }
}

// Get pending users with pagination
export const getPendingUsers = async (
  page: number = 1, 
  perPage: number = 10,
  sortBy?: string,
  sortOrder?: 'asc' | 'desc',
  search?: string,
  filters?: {
    school_name?: string;
  }
): Promise<PaginatedResponse> => {
  try {
    const response = await axiosInstance.get('/user-management/users/pending', {
      params: {
        page,
        per_page: perPage,
        sort_by: sortBy,
        sort_order: sortOrder,
        search,
        ...filters
      }
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch pending users:', error)
    throw error
  }
}

// Get a specific user by ID
export const getUser = async (userId: number): Promise<User> => {
  try {
    const response = await axiosInstance.get(`/user-management/users/${userId}`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch user:', error)
    throw error
  }
}

// Update a user
export const updateUser = async (userId: number, userData: UpdateUserRequest): Promise<User> => {
  try {
    const response = await axiosInstance.put(`/user-management/users/${userId}`, userData)
    return response.data
  } catch (error) {
    console.error('Failed to update user:', error)
    throw error
  }
}

// Delete a user (admin only)
export const deleteUser = async (userId: number): Promise<void> => {
  try {
    const response = await axiosInstance.delete(`/user-management/users/${userId}`)
    return response.data
  } catch (error) {
    console.error('Failed to delete user:', error)
    throw error
  }
}   

// Approve or reject a user (admin only)
export const approveUser = async (userId: number, isApproved: boolean = true): Promise<ApprovalResponse> => {
  try {
    const response = await axiosInstance.post(`/user-management/users/approve/${userId}`, {
      is_approved: isApproved
    })
    return response.data
  } catch (error) {
    console.error('Failed to approve/reject user:', error)
    throw error
  }
}

// Signup function for new user registration
export const signup = async (userData: CreateUserRequest): Promise<User> => {
  try {
    const response = await axiosInstance.post('/security/create_user', userData)
    return response.data
  } catch (error) {
    console.error('Signup failed:', error)
    throw error
  }
}

// Initiate password reset (forgot password)
export const forgotPassword = async (email: string): Promise<{message: string}> => {
  try {
    const response = await axiosInstance.post('/security/forgot-password', { email })
    return response.data
  } catch (error) {
    console.error('Forgot password request failed:', error)
    throw error
  }
}

// Verify reset token validity
export const verifyResetToken = async (token: string): Promise<{valid: boolean, email?: string, error?: string}> => {
  try {
    const response = await axiosInstance.get(`/security/verify-reset-token/${token}`)
    return response.data
  } catch (error: any) {
    console.error('Token verification failed:', error)
    if (error.response?.data) {
      return error.response.data
    }
    return { valid: false, error: 'Errore di verifica del token' }
  }
}

// Complete password reset with token and new password
export const resetPassword = async (token: string, password: string): Promise<{message: string}> => {
  try {
    const response = await axiosInstance.post(`/security/reset-password/${token}`, { 
      password, 
      confirm_password: password 
    })
    return response.data
  } catch (error) {
    console.error('Password reset failed:', error)
    throw error
  }
}

// Get all schools
export const getSchools = async (): Promise<string[]> => {
  try {
    const response = await axiosInstance.get('/schools/')
    return response.data.schools
  } catch (error) {
    console.error('Failed to fetch schools:', error)
    throw error
  }
}



interface Slot {
  id: number
  date: string
  time_period: string
  department: string
  gender_category: string
  notes: string | null
  total_spots: number
  max_students_per_school: number
  is_locked: boolean
  created_at: string
  updated_at: string
}

interface CreateSlotRequest {
  date: string
  time_period: string
  department: string
  gender_category: string
  notes?: string
  total_spots: number
  max_students_per_school: number
  is_locked?: boolean
  is_confirmed?: boolean
}

interface UpdateSlotRequest extends Partial<CreateSlotRequest> {}

interface SlotEnums {
  time_periods: string[]
  departments: string[]
  gender_categories: string[]
}

interface AvailableDates {
  available_dates: string[]
}

interface PaginatedSlotResponse {
  slots: Slot[]
  total: number
  pages: number
  current_page: number
  has_next: boolean
  has_prev: boolean
  filters: {
    date?: string
    time_period?: string
    department?: string
    gender_category?: string
    is_locked?: boolean
  }
  sort: {
    sort_by: string
    sort_order: string
  }
}

// Get all slots with pagination
export const getSlots = async (
  page: number = 1,
  perPage: number = 10,
  sortBy?: string,
  sortOrder?: 'asc' | 'desc',
  filters?: {
    date?: string
    time_period?: string
    department?: string
    gender_category?: string
    is_locked?: boolean
  }
): Promise<PaginatedSlotResponse> => {
  try {
    const response = await axiosInstance.get('/slots/', {
      params: {
        page,
        per_page: perPage,
        sort_by: sortBy,
        sort_order: sortOrder,
        ...filters
      }
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch slots:', error)
    throw error
  }
}

// Generate letters for a slot
export const generateLettersForSlot = async (slotId: number): Promise<Blob> => {
  try {
    const response = await axiosInstance.get(`/slots/${slotId}/generate-letters`, {
      responseType: 'blob'
    })
    return response.data
  } catch (error) {
    console.error('Failed to generate letters:', error)
    throw error
  }
}

interface SlotDetails extends Slot {
  registrations: Student[]
  waitingList: Student[]
  schoolsInfo: { name: string; studentsCount: number }[]
  registeredCount: number
  availableSpots: number
  occupied_spots: number
  is_confirmed: boolean
}

// Get a specific slot
export const getSlot = async (slotId: number): Promise<SlotDetails> => {
  try {
    const response = await axiosInstance.get(`/slots/${slotId}`)
    return {
      ...response.data,
      registrations: response.data.registrations || [],
      waitingList: response.data.waitingList || [],
      schoolsInfo: response.data.schoolsInfo || [],
      registeredCount: response.data.registrations?.length || 0,
      availableSpots: response.data.total_spots - (response.data.registrations?.length || 0)
    }
  } catch (error) {
    console.error('Failed to fetch slot:', error)
    throw error
  }
}

// Create a new slot
export const createSlot = async (slotData: CreateSlotRequest): Promise<Slot> => {
  try {
    const response = await axiosInstance.post('/slots/', slotData)
    return response.data.slot
  } catch (error) {
    console.error('Failed to create slot:', error)
    throw error
  }
}

// Update a slot
export const updateSlot = async (slotId: number, slotData: UpdateSlotRequest): Promise<Slot> => {
  try {
    const response = await axiosInstance.put(`/slots/${slotId}`, slotData)
    return response.data.slot
  } catch (error) {
    console.error('Failed to update slot:', error)
    throw error
  }
}

// Delete a slot
export const deleteSlot = async (slotId: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/slots/${slotId}`)
  } catch (error) {
    console.error('Failed to delete slot:', error)
    throw error
  }
}

// Get slot enums
export const getSlotEnums = async (): Promise<SlotEnums> => {
  try {
    const response = await axiosInstance.get('/slots/enum-values')
    return response.data
  } catch (error) {
    console.error('Failed to fetch slot enums:', error)
    throw error
  }
}

// Get available dates
export const getAvailableDates = async (): Promise<AvailableDates> => {
  try {
    const response = await axiosInstance.get('/slots/available-dates')
    return response.data
  } catch (error) {
    console.error('Failed to fetch available dates:', error)
    throw error
  }
}

// Update Student interface
interface Student {
  id: number
  first_name: string
  last_name: string
  school_class: string
  school_name: string
  gender: string // Usando "Maschio" o "Femmina" come valori
  address: string
  postal_code: string
  city: string
  landline?: string
  mobile: string
  created_at?: string
  updated_at?: string
}

export interface Enrollment {
  id: number
  student: Student
  slot_id: number
  is_in_waiting_list: boolean
  created_at?: string
  updated_at?: string
}

interface CreateEnrollmentRequest {
    student_id?: number
    first_name?: string
    last_name?: string
    school_class: string
    school_name: string
    gender: string // Usando "Maschio" o "Femmina" come valori
    address: string
    postal_code: string
    city: string
    landline?: string
    mobile: string
}

// Create enrollment
export const createEnrollment = async (slotId: number, data: CreateEnrollmentRequest): Promise<Enrollment> => {
  try {
    const response = await axiosInstance.post(`/slots/${slotId}/enrollments`, data)
    if (response.data.error === 'GENDER_NOT_ALLOWED') {
      throw new Error('Il genere selezionato non è consentito per questo slot')
    }
    return response.data.enrollment
  } catch (error: any) {
    console.error('Failed to create enrollment:', error)
    if (error.response?.data?.error === 'GENDER_NOT_ALLOWED') {
      throw new Error('Il genere selezionato non è consentito per questo slot')
    }
    throw error
  }
}

// Delete enrollment
export const deleteEnrollment = async (enrollmentId: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/slots/enrollments/${enrollmentId}`)
  } catch (error) {
    console.error('Failed to delete enrollment:', error)
    throw error
  }
}

// Update enrollment waiting list status
export const updateEnrollmentWaitingList = async (enrollmentId: number, isInWaitingList: boolean): Promise<Enrollment> => {
  try {
    const response = await axiosInstance.put(`/slots/enrollments/${enrollmentId}/waiting-list`, {
      is_in_waiting_list: isInWaitingList
    })
    return response.data.enrollment
  } catch (error) {
    console.error('Failed to update enrollment waiting list status:', error)
    throw error
  }
}

// Get slot enrollments
export const getSlotEnrollments = async (slotId: number, isWaitingList?: boolean): Promise<Enrollment[]> => {
  try {
    const response = await axiosInstance.get(`/slots/${slotId}/enrollments`, {
      params: { is_waiting_list: isWaitingList }
    })
    return response.data.enrollments
  } catch (error) {
    console.error('Failed to fetch slot enrollments:', error)
    throw error
  }
}

// Update student
export const updateStudent = async (studentId: number, data: Partial<Omit<Student, 'id' | 'created_at' | 'updated_at'>>): Promise<Student> => {
  try {
    const response = await axiosInstance.put(`/slots/students/${studentId}`, data)
    return response.data.student
  } catch (error) {
    console.error('Failed to update student:', error)
    throw error
  }
}

// Confirm slot and send notification emails
export const confirmSlot = async (slotId: number): Promise<SlotDetails> => {
  try {
    const response = await axiosInstance.post(`/slots/${slotId}/confirm`)
    return response.data
  } catch (error) {
    console.error('Failed to confirm slot:', error)
    throw error
  }
}

// Get organization contact information
export const getOrganizationInfo = async (): Promise<{
  first_name: string,
  last_name: string,
  full_name: string,
  telephone: string,
  email: string
}> => {
  try {
    const response = await axiosInstance.get('/slots/organization-info')
    return response.data
  } catch (error) {
    console.error('Failed to fetch organization info:', error)
    throw error
  }
}

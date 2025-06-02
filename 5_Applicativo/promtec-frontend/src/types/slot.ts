export enum GenderCategory {
    MIXED = 'Misto',
    BOYS = 'Solo ragazzi',
    GIRLS = 'Solo ragazze'
}

export enum Gender {
    BOY = 'Maschio',
    GIRL = 'Femmina'
}

export const isGenderAllowed = (category: GenderCategory, gender: Gender): boolean => {
    switch (category) {
        case GenderCategory.MIXED:
            return true;
        case GenderCategory.BOYS:
            return gender === Gender.BOY;
        case GenderCategory.GIRLS:
            return gender === Gender.GIRL;
        default:
            return false;
    }
}

export interface Student {
    id: number;  // Make id required
    firstName: string;
    lastName: string;
    gender: Gender;
    street: string;
    zipCode: string;
    city: string;
    phone?: string;
    mobile: string;
    school: string;
    grade: string;
    status?: StudentStatus;
    registrationDate?: string;
}

export interface SchoolInfo {
  name: string
  studentsCount: number
  contactPerson: string
  contactEmail: string
  contactPhone: string
  address: string
  logo?: string
  notes?: string
}

export interface Slot {
    id: number;
    date: string;
    time_period: string;
    department: string;
    gender_category: GenderCategory;
    notes: string | null;
    total_spots: number;
    max_students_per_school: number;
    is_locked: boolean;
    is_confirmed: boolean;
    created_at: string;
    updated_at: string;
    occupied_spots: number;
}

export interface CreateSlotRequest {
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

export interface UpdateSlotRequest extends Partial<CreateSlotRequest> {}

export interface SlotEnums {
  time_periods: string[]
  departments: string[]
  gender_categories: string[]
}

export type StudentStatus = 'pending' | 'confirmed' | 'cancelled' | 'waiting';
export interface ExtendedStudent {
    id: number;
    enrollmentId: number;
    firstName: string;
    lastName: string;
    gender: Gender;
    street: string;
    zipCode: string;
    city: string;
    phone?: string;
    mobile: string;
    school: string;
    grade: string;
    status: StudentStatus;
    registrationDate?: string;
}
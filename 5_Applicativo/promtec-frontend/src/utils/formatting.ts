export const formatDate = (dateString: string, short = false): string => {
  const options: Intl.DateTimeFormatOptions = short
    ? { day: '2-digit', month: '2-digit', year: 'numeric' }
    : { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('it-IT', options)
}

// Format date from ISO format to dd/mm/yyyy
export const formatDateToDDMMYYYY = (isoDate: string): string => {
  if (!isoDate) return ''
  const date = new Date(isoDate)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

// Convert date from dd/mm/yyyy to ISO format (yyyy-mm-dd)
export const convertDDMMYYYYToISO = (ddmmyyyyDate: string): string => {
  if (!ddmmyyyyDate) return ''
  const [day, month, year] = ddmmyyyyDate.split('/')
  return `${year}-${month}-${day}`
}

export const getPeriodText = (period: string): string => {
  switch (period) {
    case 'mattina':
      return 'Mattina (8:30 - 12:30)'
    case 'pomeriggio':
      return 'Pomeriggio (14:00 - 18:00)'
    default:
      return period
  }
}

export const getGenderText = (gender: string): string => {
  switch (gender) {
    case 'misto':
      return 'Misto'
    case 'maschile':
      return 'Solo ragazzi'
    case 'femminile':
      return 'Solo ragazze'
    default:
      return gender
  }
}

export const getSectionColor = (section: string): string => {
  switch (section) {
    case 'Informatica':
      return 'bg-blue-100 text-blue-800 border-blue-200'
    case 'Elettronica':
      return 'bg-purple-100 text-purple-800 border-purple-200'
    case 'Disegno':
      return 'bg-amber-100 text-amber-800 border-amber-200'
    case 'Chimica':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}
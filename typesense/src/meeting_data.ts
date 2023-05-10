export interface Meeting {
  id: string;
  body: string;
  meeting_dt: number; 
  address: string;
  is_cancelled: boolean;
  cancelled_dt: number;
  cancelled_reason: string;
  latestAgenda?: string[];
  latestAgendaLink?: string;
  latestMinutes?: string[];
  latestMinutesLink?: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
}



export interface RawMeeting {
  id: number;
  body: string;
  meeting_dt: number; 
  address: string;
  is_cancelled: boolean;
  cancelled_dt: number;
  cancelled_reason: string;
  latestAgenda?: string[];
  latestAgendaLink?: string;
  latestMinutes?: string[];
  latestMinutesLink?: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
}

export function isRawMeeting(target: any): target is RawMeeting {
  const requiredProps= ["id", "body", "meeting_dt", "address", "is_cancelled", "cancelled_dt", 
  "cancelled_reason", "contactPerson", "contactEmail", "contactPhone"]

  if (target === null) {
    return false
  }

  requiredProps.forEach((prop: string) => {
    if (!(prop in target)) {
      return false
    }
  })

  if ((target.is_cancelled && (!target.cancelled_dt || !target.cancelled_reason))) {
    return false
  }
  if (target.latestAgenda != undefined && target.latestAgendaLink == undefined) {
    return false
  }
  if (target.latestMinutes != undefined && target.latestMinutesLink == undefined) {
    return false
  }
  return true
}

export function getMeetingData(meetingsJson: any): Meeting[] {
  let meetings: Meeting[] = [];

  if (!Array.isArray(meetingsJson)) {
    throw new Error("meetingsJson is not an array")
  }
  
  meetingsJson.forEach((obj) => {
    try {
      if (isRawMeeting(obj)) {
        const meeting: RawMeeting = obj;
        meetings.push({...meeting, id: meeting.id.toString()})
      }
    } catch (error) {
      console.log(error)
    }
  })

  return meetings;
}
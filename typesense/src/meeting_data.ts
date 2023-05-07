export interface Meeting {
  id: string;
  body: string;
  meeting_dt: number; 
  address: string;
  is_cancelled: boolean;
  cancelled_dt: number;
  cancelled_reason: string;
  latestAgenda: string[];
  latestAgendaLink: string;
  latestMinutes: string[];
  latestMinutesLink: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
}

function isMeeting(target: any): target is Meeting {
  const requiredProps= ["id", "body", "meeting_dt", "address", "is_cancelled", "cancelled_dt", 
  "cancelled_reason", "latestAgenda", "latestAgendaLink", "latestMinutes", "latestMinutesLink", "contactPerson", "contactEmail", "contactPhone"]

  requiredProps.forEach((prop: string) => {
    if (!(prop in target)) {
      throw new Error(`Missing '${prop}' property : ${JSON.stringify(target)}`)
    }
  })

  if ((target.is_cancelled && (!target.cancelled_dt || !target.cancelled_reason))) {
    throw new Error(`cancelled meetings must have a cancelled_dt and cancelled_reason property: ${JSON.stringify(target)}`)
  }
  if (target.latestAgenda != null && target.latestAgendaLink == null) {
    throw new Error(`Meetings with agendas must have an agenda link: ${JSON.stringify(target)}`)
  }
  if (target.latestMinutes != null && target.latestMinutesLink == null) {
    throw new Error(`Meetings with agendas must have an agenda link: ${JSON.stringify(target)}`)
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
      if (isMeeting(obj)) {
        const meeting: Meeting = obj;
        meetings.push(meeting)
      }
    } catch (error) {
      console.log(error)
    }
  })

  return meetings;
}
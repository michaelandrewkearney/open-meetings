package edu.brown.cs.server.helpers;


public class MeetingData {

  
  private String id;
  private String body;
  private float meeting_dt;
  private String address;
  private float filing_dt;
  private boolean is_emergency;
  private boolean is_annual_calendar;
  private boolean is_private_notice;
  private boolean is_cancelled;
  private float cancelled_dt;
  private String cancelled_reason;
  private String latestAgenda;
  private String latestAgendaLink;
  private String latestMinutes;
  private String latestMinutesLink;
  private String contactPerson;
  private String contactEmail;
  private String contactPhone;



  public String getID() {
    return this.id;
  }
}
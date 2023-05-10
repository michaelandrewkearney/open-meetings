package edu.brown.cs.server;


import java.util.List;

public class MeetingData {

  private String id;
  private String body;
  private int meeting_dt;
  private String address;
  private int filing_dt;
  private boolean is_emergency;
  private boolean is_annual_calendar;
  private boolean is_private_notice;
  private boolean is_cancelled;
  private float cancelled_dt;
  private String cancelled_reason;
  private List<String> latestAgenda;
  private String latestAgendaLink;
  private List<String> latestMinutes;
  private String latestMinutesLink;
  private String contactPerson;
  private String contactEmail;
  private String contactPhone;



  public String getID() {
    return this.id;
  }
}
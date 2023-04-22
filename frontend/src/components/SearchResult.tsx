import { MeetingResult } from "../meetingTypes";

interface SearchResultProps {
  result: MeetingResult;
}

export default function SearchResult({ result }: SearchResultProps) {
  return (
    <div>
      <ul>
        <li>Body: {result.body}</li>
        <li>Meeting time: {result.meetingDate.toLocaleString()}</li>
        <li>Address: {result.address}</li>
        {result.isCancelled ? (
          <li>Cancelled {result.cancelledDate.toLocaleString()}</li>
        ) : (
          <></>
        )}
      </ul>
    </div>
  );
}

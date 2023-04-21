import React, { FormEvent, useState } from "react";
import "./App.css";
import SearchBar from "./components/SearchBar";

function App() {
  const [keyphrase, setKeyphrase] = useState("");

  const handleSearchSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log(`submitted search: ${keyphrase}`);
  };

  return (
    <div className="App">
      <SearchBar
        keyphrase={keyphrase}
        handleSearchValue={(value) => setKeyphrase(value)}
        handleSearchSubmit={handleSearchSubmit}
      />
    </div>
  );
}

export default App;

import React, { useState, useEffect } from "react"; // Importing React and hooks for state and lifecycle management
import axios from "axios"; // Importing Axios for making HTTP requests

export default function App() {
  const [rankings, setRankings] = useState([]); // State to hold rankings data
  const [loading, setLoading] = useState(true); // State to manage loading status

  useEffect(() => {
    // Fetch rankings from the Flask API when the component mounts
    axios.get("http://127.0.0.1:5000/rankings")  // Flask API endpoint
      .then((response) => {
        setRankings(response.data.rankings); // Update rankings state with fetched data
        setLoading(false); // Set loading to false after data is fetched
      })
      .catch((error) => {
        console.error("Error fetching rankings:", error); // Log any errors
        setLoading(false); // Set loading to false even if there's an error
      }); 
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center p-5">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-4xl">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Resume Rankings</h2>
        {loading ? (
          <p>Loading...</p> // Display loading message while data is being fetched
        ) : (
          <table className="w-full border-collapse border border-gray-200">
            <thead>
              <tr className="bg-gray-300">
                <th className="border px-4 py-2">Rank</th>
                <th className="border px-4 py-2">Candidate</th>
                <th className="border px-4 py-2">Score</th>
              </tr>
            </thead>
            <tbody>
              {rankings[0]?.map(([index, score], rank) => (
                <tr key={index} className="text-center">
                  <td className="border px-4 py-2">{rank + 1}</td> // Display rank
                  <td className="border px-4 py-2">Candidate {index + 1}</td> // Display candidate number
                  <td className="border px-4 py-2">{score.toFixed(2)}</td> // Display candidate score
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

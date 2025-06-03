import {useLocation} from 'react-router-dom';
import {useState, useEffect} from 'react';

function EditPage() {

  const location = useLocation();
  const {headers,rows} = location.state || {headers:[],rows:[]};

  const [table,setTable] = useState({headers,rows});
  const [heatmapUrl,setHeatmapUrl] = useState(null);
  const [ranking,setRanking] = useState(null);
  const [rankingError,setRankingError] = useState(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('default');
  const [validationErrors, setValidationErrors] = useState([]);

  const [playerNamesForRanking, setPlayerNamesForRanking] = useState([]);

  // Effect to update player names for ranking whenever table headers change
  useEffect(() => {
    setPlayerNamesForRanking(table.headers);
  }, [table.headers]);

  // Handler for changing cell content
  const handleCellChange = (rowIndex,colIndex,newValue) => {
    setTable(prevData => {
      const updatedRows = [...prevData.rows];
      const updatedRow = {...updatedRows[rowIndex]};
      const updatedData = [...updatedRow.data];
      updatedData[colIndex] = newValue;
      updatedRow.data = updatedData;
      updatedRows[rowIndex] = updatedRow;
      return {...prevData,rows: updatedRows};
    });
  };

  // Handler for changing header (column) names
  const handleHeaderChange = (colIdx,value) => {
    const updatedHeaders = [...table.headers];
    updatedHeaders[colIdx] = value;
    setTable({...table,headers:updatedHeaders});
  };

  // Handler for changing row (player) names
  const handleRowNameChange = (rowIdx,value) => {
    const updatedRows = [...table.rows];
    updatedRows[rowIdx] = {...updatedRows[rowIdx],name:value};
    setTable({...table,rows:updatedRows});
  };

  // Handler to export the current H2H table data to a CSV file
  const handleExport = () => {
    const headers = table.headers;
    const rows = table.rows;

    const csvRows = [];
    csvRows.push(['',...headers].join(',')); // Add header row
    rows.forEach(row => {
      csvRows.push([row.name,...row.data].join(',')); // Add data rows
    });

    const csv = csvRows.join('\n');

    const blob = new Blob([csv], {type: 'text/csv'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'league_data.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url); // Clean up the object URL
  };

  // Handler to generate a heatmap image via the Flask backend proxy
  const handleGenerateHeatmap = async () => {
    // 1. Create CSV string from current table data
    const headers = table.headers;
    const rows = table.rows;

    const csvRows = [];
    csvRows.push(['', ...headers].join(','));
    rows.forEach(row => {
      csvRows.push([row.name, ...row.data].join(','));
    });
    const csvString = csvRows.join('\n');

    // 2. Create a Blob from the CSV string to send as a file
    const blob = new Blob([csvString], {type: 'text/csv'});
    const formData = new FormData();
    // The filename 'league_data.csv' is important as the remote service expects it
    formData.append('file', blob, 'league_data.csv'); 

    try {
      // 3. Upload the CSV file to our Flask app's new upload endpoint
      // This endpoint proxies the file to the remote heatmap file receiver service
      const uploadRes = await fetch('http://localhost:5000/upload_heatmap_csv', {
        method: 'POST',
        body: formData
      });

      if (!uploadRes.ok) {
        // Attempt to parse JSON error from Flask, fallback to text if not JSON
        let errorData;
        try {
            errorData = await uploadRes.json();
        } catch (jsonError) {
            const textError = await uploadRes.text();
            alert(`Error uploading CSV for heatmap: ${uploadRes.status} ${uploadRes.statusText}\nServer Response (not JSON): ${textError.substring(0, 200)}...`);
            return;
        }
        alert(`Error uploading CSV for heatmap: ${errorData.error || 'Unknown error'}`);
        return;
      }

      // Extract the filename (basename) returned by Flask, which is used by the remote generator
      const {filename} = await uploadRes.json(); 

      // 4. Request the heatmap image from our Flask app's new request endpoint
      // This endpoint proxies the request and receives the image from the remote generator service
      const heatmapRes = await fetch('http://localhost:5000/request_heatmap_image', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          filename: filename, // Send the filename that was uploaded
          color: '#00FF00 #FFFF00 #FF0000' // Example color string for heatmap
        })
      });

      if (!heatmapRes.ok) {
        // Error will be in JSON format from our Flask app
        const {error} = await heatmapRes.json();
        alert(`Error generating heatmap: ${error}`);
        return;
      }

      // 5. Receive the image data (as a Blob) and create a URL for display
      const imageBlob = await heatmapRes.blob();
      const url = URL.createObjectURL(imageBlob);
      setHeatmapUrl(url); // Set the URL to display the image

    } catch (err) {
      alert(`Failed to generate heatmap: ${err.message}`);
    }
  };

  // Handler to generate rankings via the ranking microservice
  const handleGenerateRanking = async () => {
    try {
      const rankingTableData = table.rows.map(row => row.data);

      const res = await fetch('http://localhost:5000/rank', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          table: rankingTableData,
          algorithm: selectedAlgorithm
        })
      });

      const data = await res.json();

      if(res.ok) {
        setRanking(data.ranking);
        setRankingError(null);
      } else {
        setRanking(null);
        setRankingError(data.error || 'Unknown error occurred.');
      }

    } catch(err) {
      setRanking(null);
      setRankingError(err.message);
    }
  };

  // Handler to export ranking data to a CSV file
  const handleExportRankingData = async () => {
    if (!ranking || ranking.length === 0) {
      alert("Please generate rankings first before exporting.");
      return;
    }

    try {
      const rankingTableData = table.rows.map(row => row.data);
      
      const res = await fetch('http://localhost:5000/export_ranking', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          table: rankingTableData,
          ranking: ranking,
          playerNames: playerNamesForRanking
        })
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'league_ranking_data.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } else {
        const errorData = await res.json();
        alert(`Error exporting ranking data: ${errorData.error || 'Unknown error'}`);
      }

    } catch (err) {
      alert(`Failed to export ranking data: ${err.message}`);
    }
  };

  // Handler to validate table data via the validation microservice
  const handleValidateData = async () => {
    setValidationErrors([]); // Clear previous errors
    try {
      const res = await fetch('http://localhost:5000/validate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          headers: table.headers, 
          rows: table.rows 
        })
      });

      const data = await res.json();

      if (res.ok) {
        setValidationErrors(data.errors); // Set the array of error messages
        if (data.errors.length === 0) {
          alert("No data discrepancies found! Your table is consistent.");
        }
      } else {
        alert(`Error during validation: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Failed to validate data: ${err.message}`);
    }
  };


  return (
    <div>
      <h1>Your Table</h1>
      <dl>Click on a cell to edit its contents.</dl>
      <table border="1">

        <thead>
          <tr>
            <th></th>
            {table.headers.map((header,colIdx) => (
              <th key={colIdx}>
                <input
                  type="text"
                  value={header}
                  onChange={e => handleHeaderChange(colIdx,e.target.value)}
                />
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {table.rows.map((row,rowIdx) => (
            <tr key={rowIdx}>
              <td>
                <input
                  type="text"
                  value={row.name}
                  onChange={e => handleRowNameChange(rowIdx,e.target.value)}
                />
              </td>
              {row.data.map((cell,colIdx) => (
                <td key={colIdx}>
                  <input
                    type="text"
                    value={cell}
                    onChange={(e) => handleCellChange(rowIdx,colIdx,e.target.value)}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Action Buttons */}
      <button onClick={handleExport}>Export H2H Data to CSV</button>
      <button onClick={handleGenerateHeatmap}>Generate Heatmap</button>
      <button onClick={handleValidateData} style={{marginLeft: '1rem', background: '#e0e0e0'}}>Validate Data</button>

      {/* Display Validation Errors */}
      {validationErrors.length > 0 && (
        <div style={{marginTop: '1rem', padding: '10px', border: '1px solid red', backgroundColor: '#ffe0e0'}}>
          <h2>Validation Errors:</h2>
          <ul>
            {validationErrors.map((error, index) => (
              <li key={index} style={{color: 'red'}}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Ranking Controls */}
      <div style={{marginTop: '1rem'}}>
        <label htmlFor="algorithm-select" style={{marginRight: '0.5rem'}}>Choose Ranking Algorithm:</label>
        <select
          id="algorithm-select"
          value={selectedAlgorithm}
          onChange={(e) => setSelectedAlgorithm(e.target.value)}
          style={{padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc'}}
        >
          <option value="default">Default Algorithm</option>
          <option value="elo">Elo Ranking</option>
        </select>
        <button onClick={handleGenerateRanking} style={{marginLeft: '1rem'}}>Generate Rankings</button>
      </div>

      {/* Heatmap Display */}
      {heatmapUrl && (
        <div style={{marginTop: '1rem'}}>
          <p>Heatmap preview:</p>
          <a href={heatmapUrl} target="_blank" rel="noopener noreferrer" style={{display:'inline-block'}}>
            <img
              src={heatmapUrl}
              alt="heatmap preview"
              style={{maxWidth: '400px', height: 'auto', cursor: 'pointer', border: '1px solid #ccc'}}
            />
          </a>
        </div>
      )}

      {/* Ranking Results Display */}
      {ranking && (
        <div style={{marginTop: '1rem'}}>
          <h2>Ranking Results ({selectedAlgorithm === 'elo' ? 'Elo' : 'Default'})</h2>
          <ol>
            {ranking
              .map((score, idx) => ({
                name: playerNamesForRanking[idx] || `Player ${idx+1}`,
                score: score
              }))
              .sort((a, b) => b.score - a.score) // Sort players by score (highest first)
              .map((player, idx) => (
                <li key={idx}>
                  {player.name}: {player.score.toFixed(3)}
                </li>
              ))}
          </ol>
          <button onClick={handleExportRankingData} style={{marginTop: '0.5rem'}}>Export Ranking Data</button>
        </div>
      )}

      {/* Ranking Error Display */}
      {rankingError && <p style={{color:'red'}}>Error: {rankingError}</p>}
    </div>
  );
}

export default EditPage;
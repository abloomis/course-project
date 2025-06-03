import {useLocation} from 'react-router-dom';
import {useState} from 'react';

function EditPage() {

  const location = useLocation();
  const {headers,rows} = location.state || {headers:[],rows:[]};

  const [table,setTable] = useState({headers,rows});
  const [heatmapUrl,setHeatmapUrl] = useState(null);
  const [ranking,setRanking] = useState(null);
  const [rankingError,setRankingError] = useState(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('default'); // New state for algorithm selection

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

  const handleHeaderChange = (colIdx,value) => {
    const updatedHeaders = [...table.headers];
    updatedHeaders[colIdx] = value;
    setTable({...table,headers:updatedHeaders});
  };

  const handleRowNameChange = (rowIdx,value) => {
    const updatedRows = [...table.rows];
    updatedRows[rowIdx] = {...updatedRows[rowIdx],name:value};
    setTable({...table,rows:updatedRows});
  };

  const handleExport = () => {
    const headers = table.headers;
    const rows = table.rows;

    const csvRows = [];
    csvRows.push(['',...headers].join(','));
    rows.forEach(row => {
      csvRows.push([row.name,...row.data].join(','));
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
  };

  const handleGenerateHeatmap = async () => {
    const headers = table.headers;
    const rows = table.rows;

    const csvRows = [];
    csvRows.push(['', ...headers].join(','));
    rows.forEach(row => {
      csvRows.push([row.name, ...row.data].join(','));
    });
    const csvString = csvRows.join('\n');

    const blob = new Blob([csvString], {type: 'text/csv'});
    const formData = new FormData();
    formData.append('file', blob, 'league_data.csv');

    // It's recommended to define an environment variable for your API base URL
    // e.g., process.env.REACT_APP_API_BASE_URL instead of hardcoding localhost
    const uploadRes = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData
    });

    if (!uploadRes.ok) {
      const {error} = await uploadRes.json();
      alert(`error uploading csv: ${error}`);
      return;
    }

    const {filename} = await uploadRes.json();

    const heatmapRes = await fetch('http://localhost:5000/heatmap', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        filename,
        color: '#00FF00 #FFFF00 #FF0000'
      })
    });

    if (!heatmapRes.ok) {
      const {error} = await heatmapRes.json();
      alert(`error generating heatmap: ${error}`);
      return;
    }

    const blobImage = await heatmapRes.blob();
    const url = URL.createObjectURL(blobImage);
    setHeatmapUrl(url);
  };

  const handleGenerateRanking = async () => {
    try {
      const rankingTableData = table.rows.map(row => row.data);

      console.log("Ranking Table Data being sent to backend:", rankingTableData);
      console.log("Number of rows (players):", rankingTableData.length);
      if (rankingTableData.length > 0) {
          console.log("Number of columns in first row:", rankingTableData[0].length);
      }

      // Ensure the correct port for the ranking microservice (5050)
      const res = await fetch('http://localhost:5050/rank', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          table: rankingTableData,
          algorithm: selectedAlgorithm // Send the selected algorithm to the backend
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

      <button onClick={handleExport}>Export to a CSV file</button>
      <button onClick={handleGenerateHeatmap}>Generate Heatmap</button>

      {/* New UI elements for algorithm selection */}
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

      {ranking && (
        <div style={{marginTop: '1rem'}}>
          <h2>Ranking Results ({selectedAlgorithm === 'elo' ? 'Elo' : 'Default'})</h2>
          <ol>
            {ranking
              .map((score, idx) => ({
                // Assuming headers correlate to players. If not, adjust as needed.
                name: table.headers[idx] || table.rows[idx].name || `Player ${idx+1}`,
                score: score
              }))
              .sort((a, b) => b.score - a.score)
              .map((player, idx) => (
                <li key={idx}>
                  {player.name}: {player.score.toFixed(3)}
                </li>
              ))}
          </ol>
        </div>
      )}

      {rankingError && <p style={{color:'red'}}>Error: {rankingError}</p>}
    </div>
  );
}

export default EditPage;
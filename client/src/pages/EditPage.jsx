import {useLocation} from 'react-router-dom';
import {useState} from 'react';

function EditPage() {
    
  const location = useLocation();
  const {headers,rows} = location.state || {headers:[],rows:[]};

  const [table,setTable] = useState({headers,rows});

  // function for updating cells with H2H records
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

  // function for updating column names (cells in row index 0)
  const handleHeaderChange = (colIdx,value) => {
    const updatedHeaders = [...table.headers];
    updatedHeaders[colIdx] = value;
    setTable({...table,headers:updatedHeaders});
  };

  // function for updating row names (cells in column index 0)
  const handleRowNameChange = (rowIdx,value) => {
    const updatedRows = [...table.rows];
    updatedRows[rowIdx] = {...updatedRows[rowIdx],name:value};
    setTable({...table,rows:updatedRows});
  };

  // function for exporting to CSV files
  const handleExport = () => {
    // refresh headers and rows so that updates made to the table are included in export
    const headers = table.headers;
    const rows = table.rows;

    // --------------------------- TODO ---------------------------
    // perform validation checks here in the future
    //
    // pseudocode using a microservice called 'validate()': 
    // const warnings = validate(headers, rows);
    // if(warnings.length > 0) {
    //   alert();
    //   return;
    // }
  
    // construct a csv string starting with the header row
    const csvRows = [];
    csvRows.push(['',...headers].join(','));
    rows.forEach(row => {
      csvRows.push([row.name,...row.data].join(','));
    });

    const csv = csvRows.join('\n');
  
    // create a temp URL to hold the created csv
    const blob = new Blob([csv], {type: 'text/csv'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'league_data.csv';

    // manually click the link to begin download, then remove the 
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // ----------------- function for generating heatmaps -----------------
  const [heatmapUrl,setHeatmapUrl] = useState(null);

  const handleGenerateHeatmap = async () => {
    const headers = table.headers;
    const rows = table.rows;

    // convert table to csv string
    const csvRows = [];
    csvRows.push(['', ...headers].join(','));
    rows.forEach(row => {
      csvRows.push([row.name, ...row.data].join(','));
    });
    const csvString = csvRows.join('\n');

    // turn csv string into a file-like object
    const blob = new Blob([csvString], {type: 'text/csv'});
    const formData = new FormData();
    formData.append('file', blob, 'league_data.csv');

    // step 1: upload the csv to flask
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

    // step 2: request the heatmap using the filename
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

  // show image preview
  const blobImage = await heatmapRes.blob();
  const url = URL.createObjectURL(blobImage);
  setHeatmapUrl(url);
};
  

  // create an html table with interactable cells
  return (
    <div>
      <h1>Your Table</h1>
      <dl>Click on a cell to edit its contents.</dl>
      <table border="1">

        <thead>
          <tr>
            <th></th>
            {/* edit cells at row index 0, the column headers */}
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

          {/* edit cells at column index 0, the row headers */}
          {table.rows.map((row,rowIdx) => (
            <tr key={rowIdx}>
              <td>
                <input
                  type="text"
                  value={row.name}
                  onChange={e => handleRowNameChange(rowIdx,e.target.value)}
                />
              </td>

              {/* edit cells in the middle of the table, the head-to-head records*/}
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
    </div>
  );
}

export default EditPage;
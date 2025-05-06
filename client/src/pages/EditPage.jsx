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

      


    </div>

    
  );
}

export default EditPage;
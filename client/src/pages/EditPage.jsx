import {useLocation} from 'react-router-dom';
import {useState} from 'react';

function EditPage() {
  const location = useLocation();
  const {headers,rows} = location.state || {headers:[],rows:[]};

  const [table,setTable] = useState({headers,rows});

  const handleCellChange = (rowIdx,colIdx,value) => {
    const updatedRows = [...table.rows];
    updatedRows[rowIdx] = {
    ...updatedRows[rowIdx],
    data: [...updatedRows[rowIdx].data]
    };
    updatedRows[rowIdx].data[colIdx] = value;
    setTable({...table,rows:updatedRows});
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

  // create an html table with interactable cells
  return (
    <div>
      <h1>Edit Table</h1>
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
                    onChange={e => handleCellChange(rowIdx,colIdx,e.target.value)}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default EditPage;
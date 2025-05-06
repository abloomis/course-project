import {useLocation} from 'react-router-dom';

function EditPage() {
  const location = useLocation();
  const {headers,rows} = location.state || {headers:[],rows:[]};

  return (
    // create a table 
    
    <div>
      <h1>Your Table</h1>
      <table border="1">
        <thead>
          <tr>
            <th>Player</th>
            {headers.map((header,i) => <th key={i}>{header}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row,i) => (
            <tr key={i}>
              <td>{row.name}</td>
              {row.data.map((cell,j) => <td key={j}>{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default EditPage;
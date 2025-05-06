import {useState} from 'react';

// need useNavigate to navigate to editPage after uploading
import {useNavigate} from 'react-router-dom';

function ImportPage() {
  const [fileName,setFileName] = useState(null);
  const [error,setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if(!file) return;

    // return errors for non csv files
    if(file.type !== 'text/csv') {
      setError('Unsupported file type.');
      setFileName(null);
      return;
    }

    setFileName(file.name);
    setError(null);

    // read the csv file and create a matrix of the data
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.trim().split('\n');

      const matrix = lines.map(line => line.split(',').map(cell => cell.trim()));

      // first row is column headers, which are player names
      // start at slice(1) to skip the empty top-left corner
      const headers = matrix[0].slice(1);

      // reamining rows are in the form {name: ..., data: [...]}
      const rows = matrix.slice(1).map(row => ({
        name: row[0],
        data: row.slice(1)
      }));

      const tableData = {headers,rows};

      navigate('/edit', {state: tableData});
    };

    
    reader.readAsText(file);
  };

  return (
    <div>
      <h1>Import Data</h1>
      <p>Upload a CSV file</p>

      <input
        type="file"
        accept=".csv"
        onChange={handleFileChange}
      />

      {error && <p style={{color:'red'}}>{error}</p>}
    </div>
  );
}

export default ImportPage;

import fetch from 'node-fetch';

// function to call the heatmap microservice
export const generateHeatmap = async(req,res)=>{
  try{
    const {csv,color} = req.body;
    if(!csv)return res.status(400).json({error:'CSV data required'});

    // write CSV to a temporary file
    const filename = `table_${Date.now()}.csv`;
    const filepath = path.join('/tmp', filename);
    fs.writeFileSync(filepath, csv);

    // call Flask server
    const response = await fetch('http://localhost:5000/heatmap', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({filename, color})
    });

    if(!response.ok){
      const error = await response.text();
      return res.status(500).json({error});
    }

    // stream image back to client
    const buffer = await response.buffer();
    res.set('Content-Type','image/png');
    res.send(buffer);

    // optionally delete the temp CSV after
    fs.unlinkSync(filepath);
  }catch(err){
    res.status(500).json({error: err.message});
  }
};
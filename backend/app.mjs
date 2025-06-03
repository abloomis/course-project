import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import routes from './routes.mjs';

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());

// mount routes with /api (needed for calling flask-wrapped microservices)
app.use('/api', routes);

app.get('/', (req, res)=> {
    res.send('Backend is running');
})

const PORT = process.env.PORT || 3000;
app.listen(PORT, ()=> console.log(`Server is running on port ${PORT}`));
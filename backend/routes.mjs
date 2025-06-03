import express from 'express';
import {generateHeatmap} from './controller.mjs';

const router = express.Router();

router.post('/heatmap', generateHeatmap); // calls flask

export default router;
import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { id } = req.query;

  if (!id || Array.isArray(id)) {
    return res.status(400).json({ message: 'Invalid analysis ID' });
  }

  try {
    // Forward request to backend
    const response = await axios.get(`${BACKEND_URL}/api/analyses/${id}`);
    return res.status(200).json(response.data);
  } catch (error) {
    console.error(`Error fetching analysis ${id}:`, error);
    
    if (axios.isAxiosError(error) && error.response) {
      // Forward the status code and error message from the backend
      return res.status(error.response.status).json(error.response.data);
    }
    
    return res.status(500).json({ message: 'Failed to fetch analysis' });
  }
}

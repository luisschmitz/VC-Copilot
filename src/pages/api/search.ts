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

  const { query } = req.query;

  if (!query || Array.isArray(query)) {
    return res.status(400).json({ message: 'Invalid search query' });
  }

  try {
    // Extract pagination parameters
    const page = req.query.page ? parseInt(req.query.page as string) : 1;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;

    // Forward request to backend
    const response = await axios.get(`${BACKEND_URL}/api/search`, {
      params: { 
        query,
        page,
        limit
      }
    });

    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error searching analyses:', error);
    
    if (axios.isAxiosError(error) && error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    
    return res.status(500).json({ message: 'Failed to search analyses' });
  }
}

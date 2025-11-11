const EC2_BASE_URL = 'https://marsh-cyber-content-tool-api.me';
const LOCAL_BASE_URL = 'http://127.0.0.1:8000';

let currentBaseUrl = EC2_BASE_URL;
let isEC2Down = false;

export const getApiUrl = (endpoint) => {
  return `${currentBaseUrl}${endpoint}`;
};

export const fetchWithFallback = async (endpoint, options = {}) => {
  const fetchOptions = {
    method: 'GET',
    //headers: { 'Content-Type': 'application/json' },
    ...options,
  };
  
  if (fetchOptions.body && !(fetchOptions.body instanceof FormData)) {
    fetchOptions.headers = {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    };
  }

  if (!isEC2Down) {
    try {
      const response = await fetch(`${EC2_BASE_URL}${endpoint}`, fetchOptions);
      if (response.ok) {
        return response;
      }
      throw new Error('EC2 request failed');
    } catch (error) {
      console.warn('EC2 instance unavailable, falling back to localhost');
      isEC2Down = true;
      currentBaseUrl = LOCAL_BASE_URL;
    }
  }

  return fetch(`${LOCAL_BASE_URL}${endpoint}`, fetchOptions);
};

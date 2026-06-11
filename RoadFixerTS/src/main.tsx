import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router';
import { routing } from './Constants.tsx';
import './assets/styles/index.css'

const appRouter = createBrowserRouter([routing]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={appRouter}/>
  </StrictMode>
);

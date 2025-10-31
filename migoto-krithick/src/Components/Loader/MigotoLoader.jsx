import React from 'react'
import LoaderFull from '../Loaders/LoaderFull';
import AILoader from '../AILoader/AILoader';
import { useLoaderStore } from '../../store';
import Loader from './Loader';


function MigotoLoader() {
    const { loaderType } = useLoaderStore();
  
    if (loaderType === "none") return null;
    if (loaderType === "mini") return <AILoader />;
    if (loaderType === "full") return <Loader />;
  }

  
export default MigotoLoader
import React from 'react'
import { toast } from 'react-toastify';

const style={position: "top-right",
autoClose: 5000,
hideProgressBar: false,
closeOnClick: true,
pauseOnHover: true,
draggable: true,
progress: undefined,
theme: "dark"}


const success = (message)=>{
    toast.success(message, style);
}

const info = (message)=>{
    toast.info(message.style);
}

const error = (message)=>{
    toast.error(message.style);
}

const warning = (message)=>{
 toast.warn(message.style);
}

const functions={
    'success': success,
    'info': info,
    'error': error,
    'warn': warning
}



const Snackbars = (type,message) => {
  functions[type](message);
}

export default Snackbars





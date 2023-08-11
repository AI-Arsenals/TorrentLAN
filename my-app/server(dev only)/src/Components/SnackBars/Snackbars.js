import React from 'react'
import {Snackbar,Alert} from '@mui/material'
const CustomSnackbar = ({prop}) => {


  return (
    <Snackbar open={prop.open} onClose={prop.handleClose} autoHideDuration={prop.duration?prop.duration:4000}>
        <Alert variant="filled" severity={prop.severity?prop.severity:"success"} onClose={prop.handleClose}>
          {prop.message?prop.message:"Sample text"}
        </Alert>
    </Snackbar>
  )
}

export default CustomSnackbar






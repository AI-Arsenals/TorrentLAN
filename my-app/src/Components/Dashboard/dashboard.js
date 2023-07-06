import React from 'react'
import '../Dashboard/dashboardStyles.css'

const Dashboard = () => {
  return (
    <div className='dashboard-container'>
      <div className="children">
        Bytes downloaded
      </div>
      <div className="children">
        Bytes uploaded
      </div>
    </div>
  )
}

export default Dashboard

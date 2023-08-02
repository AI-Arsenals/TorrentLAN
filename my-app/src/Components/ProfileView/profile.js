import { useEffect, useState } from "react" 
import './profileStyles.css'
const Profile = () => {

    const [username,setUsername] = useState("")
    const [cacheSize,setCacheSize] = useState([0,0])

    const handleChange =(e)=>{
        setUsername(e.target.value)
    }

    const onSubmit=async()=>{
      
      let response = await fetch(`api/set_username?username=${username}`)
      let data = await response.json()
      console.log(data)
    }

    const fetchCacheSize = async()=>{
      let response = await fetch(`api/cache?action=size`)
      let data = await response.json()
      setCacheSize(data['content'])
    }

    useEffect(()=>{
      fetchCacheSize()
    },[])
  return (
    <div className="profile">
      <div className="username">

        <div className="username-form">

            <input type="text" onChange={handleChange} value={username} id="username-field" placeholder="new username" />
        </div>


            <button className="simpleButton username-update" onClick={onSubmit}>Update</button>
      </div>
      
      <div className="logs">
        <div className="size">
          Logs size: {cacheSize[0]}
        </div>
        <button className="simpleButton clear">Clear</button>
      </div>

      <div className="tempFiles">
        <div className="size">
          Temporary files size: {cacheSize[1]}
        </div>
        <button className="simpleButton clear">Clear</button>
      </div>
        
    </div>
  )
}

export default Profile

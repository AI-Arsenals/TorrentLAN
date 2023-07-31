import { useState } from "react" 
import './profileStyles.css'
const Profile = () => {

    const [username,setUsername] = useState("")

    const handleChange =(e)=>{
        setUsername(e.target.text)
    }
  return (
    <div className="profile">
        <form action="/api/setUserName" method="post" className="username-form">
            <input type="text" name="username" onChange={handleChange} value={username} id="username-field" />
            <button type="submit">Update</button>
        </form>
    </div>
  )
}

export default Profile

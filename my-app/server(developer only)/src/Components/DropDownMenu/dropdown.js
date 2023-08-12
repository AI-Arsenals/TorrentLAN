import React ,{useState} from 'react'
import Select from 'react-select'

import './dropdownStyles.css'
 




const DropDown = () => {
    
    const [selected, setSelected] = useState('');
    const options = [
        { value: 'games', label: 'games' },
        { value: 'music', label: 'music' },
        { value: 'movies', label: 'movies' }
      ]
  const selectionChangeHandler = (event) => {
    setSelected(event.target.value);
  };
  return (
   
        <>
            <Select options={options} value={selected} onChange={selectionChangeHandler} theme={theme => ({
      ...theme,
      borderRadius: 0,
      colors: {
        ...theme.colors,
        primary25: 'hotpink',
        primary: 'white',
        secondary: 'purple',
        neutral0: 'black',
        neutral80: '#ffffff'
      },
    })}/>
        </>
    
  )
}

export default DropDown

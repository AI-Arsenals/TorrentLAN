import React, { useEffect, useState } from 'react'


const Counter_1 = ()=>{
    const [counter, setCounter] = useState(0)
    useEffect(()=>{
        let interval = setInterval(() => {
            setCounter(counter=> counter+1)
            
        }, 1000);

        return ()=>{clearInterval(interval)}
    },[])
    return <div className="counter_1">
        {counter}
    </div>
}

const Counter_2 = ({counter})=>{
    return <div className="counter_2">
        {counter}
    </div>
}

let count_2=0;
const Temp = () => {
    
    useEffect(()=>{
        let interval = setInterval(() => {
           
            count_2+=1;
        }, 1000);

        return ()=>{clearInterval(interval)}
    },[])

  return (
    <div>
      <Counter_1/>
      <Counter_2 counter={count_2}/>
    </div>
  )
}

export default Temp

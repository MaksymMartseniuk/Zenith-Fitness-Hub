import api from "../api/api"
import {useState,useEffect} from "react"
    function Home(){
        const {notes,setNotes}=useState([])
        const {content,setContent}=useState("")
        const {title,setTitle}=useState("")

        const getNotes= async()=>{
            api.get("/api/notes/").then((res)=>res.data).then((data)=>setNotes(data))
        }
    return<div> Home </div>
} 
export default Home
import React, { useState, useEffect } from "react"; 
import { useNavigate } from "react-router-dom";

export default function VizDashboard() {

    const [Incidents, SetIncidents] = useState([]);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/list_incidents', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(resp => resp.json())
        .then(resp => SetIncidents(resp.result)) // <- only set the array in the JSON response
        .catch(error => console.log(error));
    }, []);
    
    return (
        <div>
            <p>this is a dashboard page</p>
            <li>
                <a href="/slidesCreationTool">Cyber Content Tool Page</a>
            </li>

            <div>
                {Incidents.map((data, idx) => (
                    <h3 key={idx}>
                        affected organization is {data?.affected_organization}
                    </h3>
                ))}
            </div>
        </div>
    );
}

import { useState } from "react";
import { io } from "socket.io-client";

const socket = io("ws://localhost:50000");

const App = () => {
	const [serverMessage, setServerMessage] = useState(null);
	const [messages, setMessages] = useState([]);
	const [listening, setListening] = useState(false);

	socket.on("from-server", (message) => {
        if (message.end) setListening(false);
		setMessages([...messages, message]);
	});

	const sendToServer = () => {
		setListening(true);
		socket.emit("to-server", "hello");
	};

	return (
		<div className="App">
            <h3>listening statues: {JSON.stringify(listening)}</h3>
			<button onClick={sendToServer} disabled={!!listening}>Listen</button>
            <h3>Results</h3>
			<ul>
				{messages.map((message, ind) => {
					if (message.end) return <p>========================</p>
					return <li>{JSON.stringify(message)}</li>;
				})}
			</ul>
		</div>
	);
};

export default App;

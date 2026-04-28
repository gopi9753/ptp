import axios from "axios";

function App() {
  const send = async () => {
    await axios.post(
      "http://localhost:8000/api/v1/payouts",
      {
        amount_paise: 5000,
        bank_account_id: "123"
      },
      {
        headers: {
          "Idempotency-Key": crypto.randomUUID()
        }
      }
    );
  };

  return <button onClick={send}>Send Payout</button>;
}

export default App;
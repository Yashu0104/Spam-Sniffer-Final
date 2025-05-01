import React, { useEffect, useState } from "react";
import axios from "axios";
import { gapi } from "gapi-script";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";


const CLIENT_ID = import.meta.env.VITE_REACT_APP_CLIENT_ID;
const API_KEY = import.meta.env.VITE_REACT_APP_API_KEY;
const SCOPES = import.meta.env.VITE_REACT_APP_SCOPES;

const COLORS = ["#4CAF50", "#FF6F61"]; // Green (non-spam) and Red (spam)

function GmailClient() {
  const [emails, setEmails] = useState([]);
  const [spamResults, setSpamResults] = useState({});
  const [user, setUser] = useState(null); // 👤 Store user info
  const [spamData, setSpamData] = useState({ spam: 0, nonSpam: 0 });

  useEffect(() => {
    function start() {
      gapi.client
        .init({
          apiKey: API_KEY,
          clientId: CLIENT_ID,
          scope: SCOPES,
          discoveryDocs: [
            "https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest",
          ],
        })
        .then(() => {
          console.log("GAPI client initialized");
        })
        .catch((error) => {
          console.error("Error initializing GAPI client", error);
        });
    }

    gapi.load("client:auth2", start);
  }, []);

  const handleLogin = async () => {
    try {
      const authInstance = gapi.auth2.getAuthInstance();
      const googleUser = await authInstance.signIn();
      const profile = googleUser.getBasicProfile();

      setUser({
        name: profile.getName(),
        email: profile.getEmail(),
      });

      console.log("Signed in!", profile.getName());

      if (!gapi.client.gmail) {
        await gapi.client.load("gmail", "v1");
        console.log("Gmail API loaded");
      }

      loadEmailsInBackground();
    } catch (error) {
      console.error("Error during login or Gmail API loading", error);
    }
  };

  const handleLogout = () => {
    const authInstance = gapi.auth2.getAuthInstance();
    authInstance.disconnect().then(() => {
      console.log("User signed out and disconnected.");
      setEmails([]);
      setSpamResults({});
      setUser(null);
      setSpamData({ spam: 0, nonSpam: 0 });
    });
  };

  const loadEmailsInBackground = async () => {
    if (!gapi.client.gmail || !gapi.client.gmail.users) {
      console.error("Gmail API not loaded yet.");
      return;
    }

    const query = ""; // Get all unread emails without date restriction

    try {
      const response = await gapi.client.gmail.users.messages.list({
        userId: "me",
        q: query,
      });

      if (response.result.messages) {
        const messages = response.result.messages;
        const emailDetails = await Promise.all(
          messages.map(async (message) => {
            const email = await gapi.client.gmail.users.messages.get({
              userId: "me",
              id: message.id,
              format: "full",
            });
            return email.result;
          })
        );

        setEmails(emailDetails);
        checkSpamForAllEmails(emailDetails);
      } else {
        setEmails([]);
        console.log("No unread emails found.");
      }
    } catch (error) {
      console.error("Error fetching emails", error);
    }
  };

  const checkSpamForAllEmails = async (emails) => {
    let spamCount = 0;
    let nonSpamCount = 0;

    const emailPromises = emails.map(async (email) => {
      const body = email.snippet;
      const emailId = email.id;

      try {
        const res = await axios.post("http://localhost:5000/check_spam", {
          text: body,
        });

        setSpamResults((prevResults) => ({
          ...prevResults,
          [emailId]: res.data,
        }));

        // Count spam and non-spam emails
        if (res.data.is_spam) {
          spamCount += 1;
        } else {
          nonSpamCount += 1;
        }
      } catch (error) {
        console.error("Error checking spam:", error);
      }
    });

    // Wait for all emails to be checked
    await Promise.all(emailPromises);

    setSpamData({ spam: spamCount, nonSpam: nonSpamCount });
  };

  const markAsRead = async (emailId) => {
    try {
      await gapi.client.gmail.users.messages.modify({
        userId: "me",
        id: emailId,
        removeLabelIds: ["UNREAD"],
      });
      setEmails((prev) => prev.filter((email) => email.id !== emailId));
      console.log("Email marked as read:", emailId);
    } catch (error) {
      console.error("Error marking email as read:", error);
    }
  };

  const deleteEmail = async (emailId) => {
    try {
      await gapi.client.gmail.users.messages.trash({
        userId: "me",
        id: emailId,
      });
      setEmails((prevEmails) =>
        prevEmails.filter((email) => email.id !== emailId)
      );
      console.log("Email moved to trash:", emailId);
    } catch (error) {
      console.error("Error trashing email:", error);
      alert(
        "Failed to delete email: " +
          (error?.result?.error?.message || "Unknown error")
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex">
      {/* Sidebar */}
      <div className="bg-gray-950 border-r border-gray-800 w-64 p-6 space-y-6 flex flex-col justify-between">
  <div>
    <div className="text-center mb-8">
      <h2 className="text-3xl font-bold text-[#94a3b8] uppercase tracking-wide">
        Spam Sniffer
      </h2>
    </div>
    <div className="space-y-4">
      <button
        onClick={handleLogin}
        className="w-full bg-[#94a3b8] hover:bg-[#7c8d99] text-white py-2 px-4 rounded-lg shadow-md transition-transform hover:scale-105"
      >
        Login with Gmail
      </button>
      <button
        onClick={handleLogout}
        className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg shadow-md transition-transform hover:scale-105"
      >
        Logout
      </button>
    </div>

    {/* Moved Responsive Pie Chart Here */}
    <div className="mt-10">
      <h3 className="text-md text-[#94a3b8] font-semibold mb-2 text-center">Spam Stats</h3>
      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={[
                { name: "Spam", value: spamData.spam },
                { name: "Non-Spam", value: spamData.nonSpam },
              ]}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={60}
              paddingAngle={5}
              dataKey="value"
              isAnimationActive={true}
            >
              {[{ color: COLORS[0] }, { color: COLORS[1] }].map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  </div>
</div>


      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        {/* Top bar */}
        <div className="flex justify-between items-center mb-6">
          {user && (
            <div>
              <p className="font-semibold text-xl text-[#94a3b8]">{user.name}</p>
              <p className="text-sm text-gray-400">{user.email}</p>
            </div>
          )}
          <button
            onClick={loadEmailsInBackground}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md shadow-md transition hover:scale-105"
          >
            Refresh Emails
          </button>
        </div>

        {/* Emails */}
        <div className="flex flex-col divide-y divide-gray-700 border border-gray-700 rounded-lg overflow-hidden">
          {emails.length > 0 ? (
            emails.map((email) => {
              const spamResult = spamResults[email.id];
              const from = email.payload.headers.find((h) => h.name === "From")?.value;
              const subject = email.payload.headers.find((h) => h.name === "Subject")?.value;

              return (
                <div
                  key={email.id}
                  className="bg-gray-800/60 border border-gray-700 backdrop-blur-md p-5 rounded-xl shadow-xl transition-transform transform hover:scale-[1.02]"
                >
                  <h5 className="text-lg font-medium text-[#94a3b8] mb-2">{from}</h5>
                  <p className="text-gray-300 mb-3">
                    <strong>Subject:</strong> {subject}
                  </p>
                  <pre className="text-sm text-gray-400 bg-gray-900 p-3 rounded-md max-h-32 overflow-y-auto">
                    {email.snippet}
                  </pre>

                  <div className="flex gap-3 mt-4">
                    <button
                      onClick={() => markAsRead(email.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md shadow"
                    >
                      Mark as Read
                    </button>
                    <button
                      onClick={() => deleteEmail(email.id)}
                      className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md shadow"
                    >
                      Delete
                    </button>
                  </div>

                  {spamResult && (
                    <div className="mt-4 bg-gray-900 border-l-4 border-yellow-500 p-3 rounded-md text-gray-300">
                      <p><strong>Spam?</strong> {spamResult.is_spam ? "✅ Yes" : "❌ No"}</p>
                      <p><strong>Spam Score:</strong> {spamResult.spam_score}</p>
                      <p><strong>Type:</strong> {spamResult.description}</p>
                      <p><strong>Summary:</strong> {spamResult.summary}</p>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <p className="text-center text-gray-500 col-span-3">No unread emails found.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default GmailClient;

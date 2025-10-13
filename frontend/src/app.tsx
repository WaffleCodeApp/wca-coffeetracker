import { isAmplifyConfigured } from "./amplify_config";
import { AuthenticationProvider } from "./contexts/authentication/provider";
import { useContext, useState, useEffect } from "react";
import { AuthenticationContext } from "./contexts/authentication/context";
import { apiConfig } from "./api_config";
import { Authenticator } from "@aws-amplify/ui-react";

const HelloWorld = () => {
  const { fetchWithToken, idToken } = useContext(AuthenticationContext);
  const [data, setData] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHelloWorld = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Construct the URL using apiConfig
        const url = `${apiConfig.my_container.protocol}${apiConfig.my_container.host}${apiConfig.my_container.path}/hello_world`;
        
        const response = await fetchWithToken(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.text();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        console.error('Error fetching hello world:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHelloWorld();
  }, [fetchWithToken, idToken]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#d32f2f',
        textAlign: 'center',
        padding: '20px'
      }}>
        <div style={{ marginBottom: '10px' }}>❌ Error</div>
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontSize: '24px',
      textAlign: 'center',
      padding: '20px'
    }}>
      <div style={{ marginBottom: '20px' }}>🌍 Hello World Response:</div>
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        padding: '20px', 
        borderRadius: '8px',
        border: '1px solid #ddd',
        fontFamily: 'monospace',
        fontSize: '16px'
      }}>
        {data}
      </div>
    </div>
  );
};

export const App = () => {
  // Show error if Amplify configuration failed
  if (!isAmplifyConfigured) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          fontSize: "16px",
          textAlign: "center",
          padding: "20px",
          maxWidth: "600px",
          margin: "0 auto",
        }}
      >
        <div
          style={{ marginBottom: "20px", color: "#d32f2f", fontSize: "20px" }}
        >
          ⚠️ Configuration Error
        </div>
        <div style={{ marginBottom: "20px" }}>
          Amplify configuration failed. Please check your environment variables.
        </div>
        <div style={{ fontSize: "14px", color: "#666" }}>
          See console for details and check your <code>.env</code> file.
        </div>
      </div>
    );
  }

  return (
    <Authenticator>
      <AuthenticationProvider>
        <HelloWorld />
      </AuthenticationProvider>
    </Authenticator>
  );
};

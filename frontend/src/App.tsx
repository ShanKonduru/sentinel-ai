import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Dashboard from '@/pages/Dashboard';
import AgentDetail from '@/pages/AgentDetail';
import './App.css';

const { Header, Content } = Layout;

function App() {
  return (
    <Router>
      <Layout className="min-h-screen">
        <Header className="header">
          <div className="logo">
            <h1 style={{ color: 'white', margin: 0 }}>Sentinel AI</h1>
          </div>
        </Header>
        <Content className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agent/:id" element={<AgentDetail />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  );
}

export default App;
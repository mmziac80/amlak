import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import PropertyList from './pages/PropertyList'
import PropertyDetail from './pages/PropertyDetail'
import AddProperty from './pages/AddProperty'


function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="properties" element={<PropertyList />} />
            <Route path="properties/:id" element={<PropertyDetail />} />
            <Route path="add-property" element={<AddProperty />} />
          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App


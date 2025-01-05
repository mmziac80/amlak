import { useState } from 'react'
import { Link } from 'react-router-dom'

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-purple-900 via-indigo-800 to-blue-900 border-b border-gray-800/50">
            <div className="container mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                    {/* لوگو */}
                    <Link to="/" className="flex items-center space-x-2 rtl:space-x-reverse">
                        <span className="text-2xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 font-bold">
                        E Bongah
                        </span>
                    </Link>
            
                    {/* منوی اصلی */}
                    <div className="flex items-center space-x-6 rtl:space-x-reverse">
                        {/* منوی کشویی املاک */}
                        <div className="relative">
                            <button 
                                onClick={() => setIsOpen(!isOpen)}
                                className="text-gray-200 hover:text-blue-400 transition-colors flex items-center"
                            >
                                لیست املاک
                                <svg className={`w-4 h-4 mr-1 transform transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                
                            {/* منوی کشویی */}
                            {isOpen && (
                                <div className="absolute top-full right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-2 z-50 text-right"> {/* اضافه کردن text-right */}
                                    <Link 
                                        to="/properties/sale" 
                                        className="block px-4 py-2 text-gray-800 hover:bg-blue-50 transition-colors text-right" // اضافه کردن text-right
                                        >
                                        املاک فروشی
                                    </Link>
                                    <Link 
                                        to="/properties/rent" 
                                        className="block px-4 py-2 text-gray-800 hover:bg-blue-50 transition-colors text-right"
                                        >
                                        املاک اجاره‌ای
                                    </Link>
                                    <Link 
                                        to="/properties/daily" 
                                        className="block px-4 py-2 text-gray-800 hover:bg-blue-50 transition-colors text-right"
                                        >
                                        اجاره روزانه
                                    </Link>
                                </div>
                            )}
                        </div>
            
                        <Link to="/add-property" className="text-gray-200 hover:text-blue-400 transition-colors">
                        ثبت ملک
                        </Link>

                        {/* اضافه کردن لینک جستجوی پیشرفته */}
                        <Link 
                            to="/advanced-search" 
                            className="text-gray-200 hover:text-blue-400 transition-colors flex items-center"
                        >
                            <svg 
                                className="w-5 h-5 ml-1" 
                                fill="none" 
                                stroke="currentColor" 
                                viewBox="0 0 24 24"
                                >
                                    <path 
                                        strokeLinecap="round" 
                                        strokeLinejoin="round" 
                                        strokeWidth={2} 
                                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
                                    />
                            </svg>
                            جستجوی پیشرفته
                        </Link>
                        
                        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center">
                            <span>ورود</span>
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    )
}


export default Navbar

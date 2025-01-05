function PropertyCard({ property }) {
    return (
      <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
        <img 
          src={property.image} 
          alt={property.title}
          className="w-full h-48 object-cover"
        />
        <div className="p-4">
          <h3 className="font-display text-lg font-bold text-primary-900">{property.title}</h3>
          <p className="text-gray-600 mt-2">{property.location}</p>
          <div className="mt-4 flex justify-between items-center">
            <span className="font-bold text-primary-500">{property.price}</span>
            <span className="text-sm text-gray-500">{property.type}</span>
          </div>
        </div>
      </div>
    )
  }
  
  export default PropertyCard
  
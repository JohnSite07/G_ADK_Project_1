-- Seed data for the locations table

INSERT INTO "locations" (name, description, image_url, latitude, longitude, is_featured) VALUES
('Whispering Pines Forest', 'A tranquil escape into a world of towering trees and soft, mossy ground.', '/images/forest.jpg', 45.4215, -75.6972, true),
('Crystal Creek Lake', 'Pristine waters reflecting the endless sky, perfect for a quiet paddle.', '/images/lake.jpg', 48.8566, 2.3522, true),
('Crimson Peak Mountains', 'Challenge yourself with a rewarding hike to breathtaking vistas.', '/images/mountains.jpg', 35.6895, 139.6917, true),
('Buenos Aires', 'The vibrant capital of Argentina, full of culture and history.', NULL, -34.6037, -58.3816, false),
('La Paz', 'The highest administrative capital in the world, nestled in the Andes.', NULL, -16.4897, -68.1193, false),
('Brasilia', 'The modernist capital of Brazil, a UNESCO World Heritage site.', NULL, -15.7942, -47.8825, false),
('Santiago', 'Chile''s capital, in a valley surrounded by the Andes and the Chilean Coast Range.', NULL, -33.4489, -70.6693, false),
('Bogota', 'Colombia''s high-altitude capital, with a historic center and vibrant culture.', NULL, 4.7110, -74.0721, false),
('Quito', 'Ecuador''s capital, on the slopes of the Pichincha volcano.', NULL, -0.1807, -78.4678, false),
('Georgetown', 'Guyana''s capital, known for its British colonial architecture.', NULL, 6.8013, -58.1551, false),
('Asuncion', 'The capital of Paraguay, on the banks of the Paraguay River.', NULL, -25.2637, -57.5759, false),
('Paramaribo', 'Suriname''s capital, with a historic inner city that is a UNESCO World Heritage site.', NULL, 5.8520, -55.2038, false),
('Montevideo', 'Uruguay''s capital, with a rich cultural life and a beautiful old town.', NULL, -34.9011, -56.1645, false),
('Caracas', 'Venezuela''s capital, a commercial and cultural center located in a northern mountain valley.', NULL, 10.4806, -66.9036, false),
('Lima', 'Peru''s capital, a sprawling metropolis and one of South America''s largest cities.', NULL, -12.0464, -77.0428, false);

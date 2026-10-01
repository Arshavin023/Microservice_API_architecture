--
-- PostgreSQL database dump
--

\restrict KReKUMsDPi0HVg8UCpwSuwXfwDWNmnG1xkg3WcBUDCQaw3MYW81KPhfgVHRrj37

-- Dumped from database version 18.6 (Ubuntu 18.6-1.pgdg24.04+2)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-1.pgdg24.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: microservices
--

COPY public.alembic_version (version_num) FROM stdin;
402a49630f56
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: microservices
--

COPY public.categories (id, name, display_order, is_active, created_at, updated_at, description) FROM stdin;
672c6e52-886e-452b-97aa-952c6a0aec1e	Rice Dishes	1	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	Nigerian rice specialties
b40ca01a-c465-4b5f-9723-2b3c421ff730	Soups	2	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	Traditional Nigerian soups
7345a947-65b9-4031-b37c-7b1d311eb01f	Swallow	3	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	Fufu, eba, semo and more
2dbd31e3-edcf-46c0-ba26-bf6348694a78	Sides & Extras	4	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	Extras, small chops and sides
d85700f2-c7d5-49b8-a176-1f46d53c40e6	Proteins	5	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	Add-on proteins for your meal
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: microservices
--

COPY public.products (id, category_id, name, description, is_available, created_at, updated_at, image_url) FROM stdin;
5c1f066a-50fb-40dd-8993-c9e83e0fab65	672c6e52-886e-452b-97aa-952c6a0aec1e	Party Jollof Rice	Smoky party-style jollof rice cooked in rich tomato and pepper stew over firewood. The real deal.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?auto=format&fit=crop&w=600&q=80
f912ec25-96e4-4162-b50d-37d627204ad5	672c6e52-886e-452b-97aa-952c6a0aec1e	Fried Rice	Nigerian-style stir-fried rice with mixed vegetables, curry, liver, green peas, and shrimp.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=600&q=80
44c4233d-ec5b-469a-b950-48d03bc824f1	b40ca01a-c465-4b5f-9723-2b3c421ff730	Egusi Soup	Ground melon seeds cooked with assorted meat, stockfish, crayfish, and ugu leaves in palm oil. Best with swallow.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=600&q=80
a0f87fff-2bdb-497d-8f9a-c6dcd2e4c250	b40ca01a-c465-4b5f-9723-2b3c421ff730	Vegetable Soup	Fresh ugu and waterleaf cooked with palm oil, crayfish, stockfish, and assorted meat.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=600&q=80
af987bc0-0fef-47be-8fb8-5536156e6061	b40ca01a-c465-4b5f-9723-2b3c421ff730	Afang Soup	Cross River delicacy — afang leaves with waterleaf, periwinkle, assorted meat, and crayfish in rich palm oil.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80
493e3e54-e1b2-4ffb-b293-76928ea798e7	b40ca01a-c465-4b5f-9723-2b3c421ff730	Ogbono Soup	Draw soup made with ground ogbono seeds, assorted meat, crayfish, and vegetables. Silky and satisfying.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=600&q=80
92dbdb3d-6c7f-4f5e-ab5b-01bd591dab4d	b40ca01a-c465-4b5f-9723-2b3c421ff730	Bitterleaf Soup	Washed bitterleaf cooked with cocoyam, assorted meat, stockfish, and crayfish. An Igbo classic.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&q=80
de511030-2f0d-459e-aeb6-3cae33504768	7345a947-65b9-4031-b37c-7b1d311eb01f	Eba	Firm garri swallow. Order with any soup.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=600&q=80
5eacd92d-dd3a-438f-998d-94883cb8d06f	7345a947-65b9-4031-b37c-7b1d311eb01f	Fufu	Smooth pounded cassava swallow. Best with draw soups.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=600&q=80
47d470e9-a9ed-4bd6-bbe1-3b8c951a4174	7345a947-65b9-4031-b37c-7b1d311eb01f	Semo	Soft semolina swallow with a neutral taste that pairs with any soup.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1616070829624-88405a603c96?auto=format&fit=crop&w=600&q=80
a4b60850-45f3-40c3-a147-b58dc2f09929	7345a947-65b9-4031-b37c-7b1d311eb01f	Wheat Flour Meal	Whole wheat swallow with a slightly earthy flavour and smooth texture.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80
bd0466d0-9f5c-440d-968b-a5b22f634529	2dbd31e3-edcf-46c0-ba26-bf6348694a78	Moi Moi	Steamed bean pudding with peppers, onions, eggs, and fish. Soft, savoury, and filling.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=600&q=80
15420485-ef8d-49ba-b3fa-7a54fc3dcdec	2dbd31e3-edcf-46c0-ba26-bf6348694a78	Beans and Plantain	Peppered brown beans cooked with palm oil and onions, served with sweet fried plantain (dodo).	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1541832676-9b763b0239ab?auto=format&fit=crop&w=600&q=80
76156d0e-5260-47df-bec7-842562a4b2d5	2dbd31e3-edcf-46c0-ba26-bf6348694a78	Fried Plantain (Dodo)	Golden sweet ripe plantain slices, fried to perfection. Great as a side with any meal.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1628191010210-a59de33e56b6?auto=format&fit=crop&w=600&q=80
97dfb52d-3823-4355-9999-021d3c809a9f	d85700f2-c7d5-49b8-a176-1f46d53c40e6	Beef	Seasoned and slow-cooked beef pieces. Add to any meal.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80
29ddfd05-a07f-47bd-aab0-14b9ba69afbd	d85700f2-c7d5-49b8-a176-1f46d53c40e6	Chicken	Peppered or grilled chicken. Choose your size.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?auto=format&fit=crop&w=600&q=80
5c46e131-b519-45ed-85de-efc9cb1c498e	d85700f2-c7d5-49b8-a176-1f46d53c40e6	Turkey	Oven-roasted turkey pieces, richly seasoned.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1518492104633-130d0cc84637?auto=format&fit=crop&w=600&q=80
30a11ec7-60d4-478b-9d4c-f1d205e600b4	d85700f2-c7d5-49b8-a176-1f46d53c40e6	Fish	Seasoned fried or grilled fish. Tilapia or catfish available.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=600&q=80
1db7da2e-4409-4af8-8a3d-93e7faa342f9	d85700f2-c7d5-49b8-a176-1f46d53c40e6	Goat Meat	Tender peppered goat meat, slow-cooked to perfection.	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087	https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?auto=format&fit=crop&w=600&q=80
\.


--
-- Data for Name: product_variants; Type: TABLE DATA; Schema: public; Owner: microservices
--

COPY public.product_variants (id, product_id, size, price, is_available, created_at, updated_at) FROM stdin;
4b135717-adcb-4fd8-818e-8672adddcd55	5c1f066a-50fb-40dd-8993-c9e83e0fab65	small	1800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
1a40c15f-a790-4cb4-b355-3cf718dc91be	5c1f066a-50fb-40dd-8993-c9e83e0fab65	medium	2800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
53b9b7f5-58af-4f92-bd2e-497eacfad176	5c1f066a-50fb-40dd-8993-c9e83e0fab65	large	4500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
dce61263-5798-40e8-8fdb-13b25b61cd56	f912ec25-96e4-4162-b50d-37d627204ad5	small	1800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
45bf2678-18d5-49d0-bfa5-72648814e436	f912ec25-96e4-4162-b50d-37d627204ad5	medium	2800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
78ebdca0-39aa-4fea-93fe-dacf786063a8	f912ec25-96e4-4162-b50d-37d627204ad5	large	4500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
1a63f163-631c-4a21-bfa4-47e042e24eb0	44c4233d-ec5b-469a-b950-48d03bc824f1	small	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
18ed31e2-5782-48d0-a8db-1cb1fb7fee48	44c4233d-ec5b-469a-b950-48d03bc824f1	medium	2500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
a1ddbb33-9cb5-4633-8255-928d63bbba95	44c4233d-ec5b-469a-b950-48d03bc824f1	large	4000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
365dd89b-7747-481a-92ab-a9ea937afa5d	a0f87fff-2bdb-497d-8f9a-c6dcd2e4c250	small	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
c7531eee-3c4e-4215-a9e5-5ca48e7a858d	a0f87fff-2bdb-497d-8f9a-c6dcd2e4c250	medium	2500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
0b7a4275-1aac-41de-88b2-79666a17ea52	a0f87fff-2bdb-497d-8f9a-c6dcd2e4c250	large	4000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
0f9f63d6-b0e0-4628-b322-5ca853023578	af987bc0-0fef-47be-8fb8-5536156e6061	small	1800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
3d41defd-ebd5-4450-802e-c69b3d32cbf8	af987bc0-0fef-47be-8fb8-5536156e6061	medium	3000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
bed9a826-b4b1-45dd-b18b-835b491f83f4	af987bc0-0fef-47be-8fb8-5536156e6061	large	5000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
4aa84744-a83a-42e9-8295-c551e6fdb196	493e3e54-e1b2-4ffb-b293-76928ea798e7	small	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
5bdd90da-f605-4452-801d-c00d43407967	493e3e54-e1b2-4ffb-b293-76928ea798e7	medium	2500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
3e49c75c-d7bd-4876-93f6-70a079d71c70	493e3e54-e1b2-4ffb-b293-76928ea798e7	large	4000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
2405b7b8-8c51-474e-966b-8280f8945734	92dbdb3d-6c7f-4f5e-ab5b-01bd591dab4d	small	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
f77f3dcc-966b-4185-9add-63381777d285	92dbdb3d-6c7f-4f5e-ab5b-01bd591dab4d	medium	2500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
6788c907-9cb0-4e45-834c-8af05d74f8d3	92dbdb3d-6c7f-4f5e-ab5b-01bd591dab4d	large	4000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
cf8d894e-1524-457b-bc37-13dc97d36193	de511030-2f0d-459e-aeb6-3cae33504768	portion	500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
b4c8f17c-9f02-4def-bbf9-01c85e9bad30	5eacd92d-dd3a-438f-998d-94883cb8d06f	portion	500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
0771cc57-d46e-4c2a-b43e-45bb712616fd	47d470e9-a9ed-4bd6-bbe1-3b8c951a4174	portion	500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
cb2e7fe1-ac6a-4c43-95be-d5deacbe6b17	a4b60850-45f3-40c3-a147-b58dc2f09929	portion	600.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
5550b521-1470-4246-94a9-cfbd5e22d8f5	bd0466d0-9f5c-440d-968b-a5b22f634529	small	700.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
6e870345-51b6-4bd7-a5d3-7ca467d3a07e	bd0466d0-9f5c-440d-968b-a5b22f634529	large	1200.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
5f83bf49-f956-44b1-aee0-b4d8734de643	15420485-ef8d-49ba-b3fa-7a54fc3dcdec	regular	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
83b1f4e6-3964-4108-a647-ea2ff337418f	15420485-ef8d-49ba-b3fa-7a54fc3dcdec	large	2500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
0a786c1c-74d0-4e21-b6cc-bdaf92b92a07	76156d0e-5260-47df-bec7-842562a4b2d5	small	600.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
df22431e-3bd1-42ef-b2ec-c49656c80cb2	76156d0e-5260-47df-bec7-842562a4b2d5	regular	900.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
0ca7e465-c42e-4ccd-a331-c05899dfbb8b	76156d0e-5260-47df-bec7-842562a4b2d5	large	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
20ab8cfb-c244-45b4-b97c-97cb6af94c08	97dfb52d-3823-4355-9999-021d3c809a9f	small	800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
a115bdbf-49c3-4f95-890d-a93f1989965f	97dfb52d-3823-4355-9999-021d3c809a9f	large	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
b9450e3c-f657-4301-a13c-0e6931249bac	29ddfd05-a07f-47bd-aab0-14b9ba69afbd	half	1500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
4d6de8eb-67b0-4f89-924b-a2b6266b6544	29ddfd05-a07f-47bd-aab0-14b9ba69afbd	full	2800.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
2d029d0b-cc68-4cc7-bfef-e42c6807e351	5c46e131-b519-45ed-85de-efc9cb1c498e	small	2000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
c89c4be9-19d1-4d21-aa01-012666413429	5c46e131-b519-45ed-85de-efc9cb1c498e	large	3500.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
4833dbbe-6195-4463-9de2-55c13d64b5a8	30a11ec7-60d4-478b-9d4c-f1d205e600b4	small	1000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
adebad5c-e38f-494a-bdfc-af9eab013b13	30a11ec7-60d4-478b-9d4c-f1d205e600b4	large	2000.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
0fce8420-6a2b-4ea6-89a1-25b05ec1e4c4	1db7da2e-4409-4af8-8a3d-93e7faa342f9	small	1200.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
728370b9-8dc2-4e34-9606-f7b74f777962	1db7da2e-4409-4af8-8a3d-93e7faa342f9	large	2200.00	t	2026-08-17 01:35:24.247087	2026-08-17 01:35:24.247087
\.


--
-- PostgreSQL database dump complete
--

\unrestrict KReKUMsDPi0HVg8UCpwSuwXfwDWNmnG1xkg3WcBUDCQaw3MYW81KPhfgVHRrj37


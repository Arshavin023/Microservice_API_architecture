-- Pizzasale Nigerian Menu Seed
-- Run: sudo -u postgres psql -d product_service_db -f seed_nigerian_menu.sql

BEGIN;

DELETE FROM product_variants;
DELETE FROM products;
DELETE FROM categories;

-- ── Categories ──────────────────────────────────────────────────────────────
INSERT INTO categories (id, name, description, is_active, display_order, created_at, updated_at) VALUES
  (gen_random_uuid(), 'Rice Dishes',   'Nigerian rice specialties',           true, 1, now(), now()),
  (gen_random_uuid(), 'Soups',         'Traditional Nigerian soups',          true, 2, now(), now()),
  (gen_random_uuid(), 'Swallow',       'Fufu, eba, semo and more',            true, 3, now(), now()),
  (gen_random_uuid(), 'Sides & Extras','Extras, small chops and sides',       true, 4, now(), now()),
  (gen_random_uuid(), 'Proteins',      'Add-on proteins for your meal',       true, 5, now(), now());

-- ── RICE DISHES ─────────────────────────────────────────────────────────────

-- 1. Party Jollof Rice
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Rice Dishes'),
       'Party Jollof Rice',
       'Smoky party-style jollof rice cooked in rich tomato and pepper stew over firewood. The real deal.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1800.00, true, now(), now() FROM products WHERE name = 'Party Jollof Rice'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 2800.00, true, now(), now() FROM products WHERE name = 'Party Jollof Rice'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  4500.00, true, now(), now() FROM products WHERE name = 'Party Jollof Rice';

-- 2. Fried Rice
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Rice Dishes'),
       'Fried Rice',
       'Nigerian-style stir-fried rice with mixed vegetables, curry, liver, green peas, and shrimp.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1800.00, true, now(), now() FROM products WHERE name = 'Fried Rice'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 2800.00, true, now(), now() FROM products WHERE name = 'Fried Rice'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  4500.00, true, now(), now() FROM products WHERE name = 'Fried Rice';

-- ── SOUPS ───────────────────────────────────────────────────────────────────

-- 3. Egusi Soup
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Soups'),
       'Egusi Soup',
       'Ground melon seeds cooked with assorted meat, stockfish, crayfish, and ugu leaves in palm oil. Best with swallow.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1500.00, true, now(), now() FROM products WHERE name = 'Egusi Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 2500.00, true, now(), now() FROM products WHERE name = 'Egusi Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  4000.00, true, now(), now() FROM products WHERE name = 'Egusi Soup';

-- 4. Vegetable Soup
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Soups'),
       'Vegetable Soup',
       'Fresh ugu and waterleaf cooked with palm oil, crayfish, stockfish, and assorted meat.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1500.00, true, now(), now() FROM products WHERE name = 'Vegetable Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 2500.00, true, now(), now() FROM products WHERE name = 'Vegetable Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  4000.00, true, now(), now() FROM products WHERE name = 'Vegetable Soup';

-- 5. Afang Soup
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Soups'),
       'Afang Soup',
       'Cross River delicacy — afang leaves with waterleaf, periwinkle, assorted meat, and crayfish in rich palm oil.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1800.00, true, now(), now() FROM products WHERE name = 'Afang Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 3000.00, true, now(), now() FROM products WHERE name = 'Afang Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  5000.00, true, now(), now() FROM products WHERE name = 'Afang Soup';

-- 6. Ogbono Soup
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Soups'),
       'Ogbono Soup',
       'Draw soup made with ground ogbono seeds, assorted meat, crayfish, and vegetables. Silky and satisfying.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1500.00, true, now(), now() FROM products WHERE name = 'Ogbono Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 2500.00, true, now(), now() FROM products WHERE name = 'Ogbono Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  4000.00, true, now(), now() FROM products WHERE name = 'Ogbono Soup';

-- 7. Bitterleaf Soup
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Soups'),
       'Bitterleaf Soup',
       'Washed bitterleaf cooked with cocoyam, assorted meat, stockfish, and crayfish. An Igbo classic.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1500.00, true, now(), now() FROM products WHERE name = 'Bitterleaf Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'medium'::sizeenum, 2500.00, true, now(), now() FROM products WHERE name = 'Bitterleaf Soup'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  4000.00, true, now(), now() FROM products WHERE name = 'Bitterleaf Soup';

-- ── SWALLOW ─────────────────────────────────────────────────────────────────

-- Each swallow is a separate product with one size (portion)

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Swallow'),
       'Eba', 'Firm garri swallow. Order with any soup.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'portion'::sizeenum, 500.00, true, now(), now() FROM products WHERE name = 'Eba';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Swallow'),
       'Fufu', 'Smooth pounded cassava swallow. Best with draw soups.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'portion'::sizeenum, 500.00, true, now(), now() FROM products WHERE name = 'Fufu';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Swallow'),
       'Semo', 'Soft semolina swallow with a neutral taste that pairs with any soup.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'portion'::sizeenum, 500.00, true, now(), now() FROM products WHERE name = 'Semo';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Swallow'),
       'Wheat Flour Meal', 'Whole wheat swallow with a slightly earthy flavour and smooth texture.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'portion'::sizeenum, 600.00, true, now(), now() FROM products WHERE name = 'Wheat Flour Meal';

-- ── SIDES & EXTRAS ───────────────────────────────────────────────────────────

-- 8. Moi Moi
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Sides & Extras'),
       'Moi Moi',
       'Steamed bean pudding with peppers, onions, eggs, and fish. Soft, savoury, and filling.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  700.00, true, now(), now() FROM products WHERE name = 'Moi Moi'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum, 1200.00, true, now(), now() FROM products WHERE name = 'Moi Moi';

-- 9. Beans and Plantain
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Sides & Extras'),
       'Beans and Plantain',
       'Peppered brown beans cooked with palm oil and onions, served with sweet fried plantain (dodo).',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'regular'::sizeenum, 1500.00, true, now(), now() FROM products WHERE name = 'Beans and Plantain'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,   2500.00, true, now(), now() FROM products WHERE name = 'Beans and Plantain';

-- 10. Fried Plantain
INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(),
       (SELECT id FROM categories WHERE name = 'Sides & Extras'),
       'Fried Plantain (Dodo)',
       'Golden sweet ripe plantain slices, fried to perfection. Great as a side with any meal.',
       true, now(), now();

INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,   600.00, true, now(), now() FROM products WHERE name = 'Fried Plantain (Dodo)'
UNION ALL
SELECT gen_random_uuid(), id, 'regular'::sizeenum, 900.00, true, now(), now() FROM products WHERE name = 'Fried Plantain (Dodo)'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  1500.00, true, now(), now() FROM products WHERE name = 'Fried Plantain (Dodo)';

-- ── PROTEINS ────────────────────────────────────────────────────────────────

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Proteins'),
       'Beef', 'Seasoned and slow-cooked beef pieces. Add to any meal.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  800.00, true, now(), now() FROM products WHERE name = 'Beef'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum, 1500.00, true, now(), now() FROM products WHERE name = 'Beef';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Proteins'),
       'Chicken', 'Peppered or grilled chicken. Choose your size.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'half'::sizeenum,  1500.00, true, now(), now() FROM products WHERE name = 'Chicken'
UNION ALL
SELECT gen_random_uuid(), id, 'full'::sizeenum,  2800.00, true, now(), now() FROM products WHERE name = 'Chicken';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Proteins'),
       'Turkey', 'Oven-roasted turkey pieces, richly seasoned.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  2000.00, true, now(), now() FROM products WHERE name = 'Turkey'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  3500.00, true, now(), now() FROM products WHERE name = 'Turkey';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Proteins'),
       'Fish', 'Seasoned fried or grilled fish. Tilapia or catfish available.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1000.00, true, now(), now() FROM products WHERE name = 'Fish'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  2000.00, true, now(), now() FROM products WHERE name = 'Fish';

INSERT INTO products (id, category_id, name, description, is_available, created_at, updated_at)
SELECT gen_random_uuid(), (SELECT id FROM categories WHERE name = 'Proteins'),
       'Goat Meat', 'Tender peppered goat meat, slow-cooked to perfection.', true, now(), now();
INSERT INTO product_variants (id, product_id, size, price, is_available, created_at, updated_at)
SELECT gen_random_uuid(), id, 'small'::sizeenum,  1200.00, true, now(), now() FROM products WHERE name = 'Goat Meat'
UNION ALL
SELECT gen_random_uuid(), id, 'large'::sizeenum,  2200.00, true, now(), now() FROM products WHERE name = 'Goat Meat';

COMMIT;

-- ── Verify ──────────────────────────────────────────────────────────────────
SELECT
  c.name AS category,
  p.name AS product,
  string_agg(v.size || ' ₦' || v.price::int, ' · ' ORDER BY v.price) AS variants
FROM products p
JOIN categories c ON p.category_id = c.id
JOIN product_variants v ON v.product_id = p.id
GROUP BY c.display_order, c.name, p.name
ORDER BY c.display_order, p.name;

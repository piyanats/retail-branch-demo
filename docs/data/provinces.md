# Province & Location Master Data

## Overview

ข้อมูล Master Data สำหรับจังหวัด อำเภอ/เขต ตำบล/แขวง และรหัสไปรษณีย์ ของประเทศไทย ใช้สำหรับ dropdown และ validation ใน forms ต่างๆ

## Database Schema

### Table: `provinces`

```sql
CREATE TABLE retail_branches.provinces (
  province_id STRING NOT NULL,              -- รหัสจังหวัด (2 หลัก)
  province_name_th STRING NOT NULL,         -- ชื่อจังหวัด (ไทย)
  province_name_en STRING,                  -- ชื่อจังหวัด (อังกฤษ)
  region STRING NOT NULL                    -- ภูมิภาค (central, north, northeast, south, east, west)
);
```

### Table: `districts`

```sql
CREATE TABLE retail_branches.districts (
  district_id STRING NOT NULL,              -- รหัสอำเภอ/เขต
  district_name_th STRING NOT NULL,         -- ชื่ออำเภอ/เขต (ไทย)
  district_name_en STRING,                  -- ชื่ออำเภอ/เขต (อังกฤษ)
  province_id STRING NOT NULL,              -- รหัสจังหวัด (FK)
  district_type STRING                      -- ประเภท (district, amphoe, khet)
);
```

### Table: `subdistricts`

```sql
CREATE TABLE retail_branches.subdistricts (
  subdistrict_id STRING NOT NULL,           -- รหัสตำบล/แขวง
  subdistrict_name_th STRING NOT NULL,      -- ชื่อตำบล/แขวง (ไทย)
  subdistrict_name_en STRING,               -- ชื่อตำบล/แขวง (อังกฤษ)
  district_id STRING NOT NULL,              -- รหัสอำเภอ/เขต (FK)
  postal_code STRING                        -- รหัสไปรษณีย์
);
```

## Data Source

**Primary Source:**
- [Thailand Postal Code Database](https://github.com/Cerberus/thailand-postcodes)
- กรมการปกครอง กระทรวงมหาดไทย

**Total Records:**
- Provinces: 77
- Districts/Amphoes: ~928
- Subdistricts/Tambons: ~7,255

## API Endpoints

### GET `/api/master-data/provinces`

ดึงรายการจังหวัดทั้งหมด

**Query Parameters:**
- `region` (optional): กรองตามภูมิภาค

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "province_id": "10",
      "province_name_th": "กรุงเทพมหานคร",
      "province_name_en": "Bangkok",
      "region": "central"
    },
    {
      "province_id": "50",
      "province_name_th": "เชียงใหม่",
      "province_name_en": "Chiang Mai",
      "region": "north"
    }
  ]
}
```

### GET `/api/master-data/districts`

ดึงรายการอำเภอ/เขต

**Query Parameters:**
- `province_id` (required): รหัสจังหวัด

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "district_id": "1001",
      "district_name_th": "เขตพระนคร",
      "district_name_en": "Phra Nakhon",
      "province_id": "10",
      "district_type": "khet"
    },
    {
      "district_id": "1002",
      "district_name_th": "เขตดุสิต",
      "district_name_en": "Dusit",
      "province_id": "10",
      "district_type": "khet"
    }
  ]
}
```

### GET `/api/master-data/subdistricts`

ดึงรายการตำบล/แขวง

**Query Parameters:**
- `district_id` (required): รหัสอำเภอ/เขต

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "subdistrict_id": "100101",
      "subdistrict_name_th": "พระบรมมหาราชวัง",
      "subdistrict_name_en": "Phra Borom Maha Ratchawang",
      "district_id": "1001",
      "postal_code": "10200"
    },
    {
      "subdistrict_id": "100102",
      "subdistrict_name_th": "วังบูรพาภิรมย์",
      "subdistrict_name_en": "Wang Burapha Phirom",
      "district_id": "1001",
      "postal_code": "10200"
    }
  ]
}
```

### GET `/api/master-data/postal-codes/{postal_code}`

ค้นหาข้อมูลจากรหัสไปรษณีย์

**Response:**
```json
{
  "success": true,
  "data": {
    "postal_code": "10200",
    "locations": [
      {
        "province_name_th": "กรุงเทพมหานคร",
        "district_name_th": "เขตพระนคร",
        "subdistrict_name_th": "พระบรมมหาราชวัง"
      },
      {
        "province_name_th": "กรุงเทพมหานคร",
        "district_name_th": "เขตพระนคร",
        "subdistrict_name_th": "วังบูรพาภิรมย์"
      }
    ]
  }
}
```

## Frontend Implementation

### Cascading Dropdowns (จังหวัด → อำเภอ → ตำบล)

```javascript
// Initialize province dropdown
async function initLocationDropdowns() {
  const provinceSelect = document.getElementById('province');
  const districtSelect = document.getElementById('district');
  const subdistrictSelect = document.getElementById('subdistrict');
  const postalCodeInput = document.getElementById('postal_code');

  // Load provinces
  const provinces = await API.get('/api/master-data/provinces');
  provinceSelect.innerHTML = '<option value="">-- เลือกจังหวัด --</option>';
  provinces.data.forEach(province => {
    provinceSelect.innerHTML += `
      <option value="${province.province_id}">
        ${province.province_name_th}
      </option>
    `;
  });

  // Province change -> Load districts
  provinceSelect.addEventListener('change', async (e) => {
    const provinceId = e.target.value;

    // Reset dependent fields
    districtSelect.innerHTML = '<option value="">-- เลือกอำเภอ/เขต --</option>';
    subdistrictSelect.innerHTML = '<option value="">-- เลือกตำบล/แขวง --</option>';
    postalCodeInput.value = '';

    if (!provinceId) return;

    // Load districts
    const districts = await API.get('/api/master-data/districts', {
      province_id: provinceId
    });

    districts.data.forEach(district => {
      districtSelect.innerHTML += `
        <option value="${district.district_id}">
          ${district.district_name_th}
        </option>
      `;
    });
  });

  // District change -> Load subdistricts
  districtSelect.addEventListener('change', async (e) => {
    const districtId = e.target.value;

    // Reset dependent fields
    subdistrictSelect.innerHTML = '<option value="">-- เลือกตำบล/แขวง --</option>';
    postalCodeInput.value = '';

    if (!districtId) return;

    // Load subdistricts
    const subdistricts = await API.get('/api/master-data/subdistricts', {
      district_id: districtId
    });

    subdistricts.data.forEach(subdistrict => {
      subdistrictSelect.innerHTML += `
        <option value="${subdistrict.subdistrict_id}" data-postal="${subdistrict.postal_code}">
          ${subdistrict.subdistrict_name_th}
        </option>
      `;
    });
  });

  // Subdistrict change -> Auto-fill postal code
  subdistrictSelect.addEventListener('change', (e) => {
    const selectedOption = e.target.selectedOptions[0];
    const postalCode = selectedOption?.dataset.postal;
    if (postalCode) {
      postalCodeInput.value = postalCode;
    }
  });
}
```

### Auto-complete Location Search

```javascript
// Auto-complete for location search
const locationInput = document.getElementById('locationSearch');

const searchLocations = debounce(async (query) => {
  if (query.length < 2) return;

  const results = await API.get('/api/master-data/search', { q: query });

  // Show autocomplete dropdown
  showAutocomplete(results.data);
}, 300);

locationInput.addEventListener('input', (e) => {
  searchLocations(e.target.value);
});
```

## Data Seeding

### Script: Load Province Data

```python
# scripts/seed_provinces.py

import json
from google.cloud import bigquery
import os

def load_provinces():
    """Load province data from JSON file to BigQuery"""

    client = bigquery.Client()
    dataset_id = 'retail_branches'

    # Load JSON data
    with open('data/provinces.json', 'r', encoding='utf-8') as f:
        provinces = json.load(f)

    # Insert into BigQuery
    table_id = f"{client.project}.{dataset_id}.provinces"
    errors = client.insert_rows_json(table_id, provinces)

    if errors:
        print(f"Errors: {errors}")
    else:
        print(f"Loaded {len(provinces)} provinces")

def load_districts():
    """Load district data"""
    # Similar implementation

def load_subdistricts():
    """Load subdistrict data"""
    # Similar implementation

if __name__ == "__main__":
    load_provinces()
    load_districts()
    load_subdistricts()
```

### Data File Format (data/provinces.json)

```json
[
  {
    "province_id": "10",
    "province_name_th": "กรุงเทพมหานคร",
    "province_name_en": "Bangkok",
    "region": "central"
  },
  {
    "province_id": "11",
    "province_name_th": "สมุทรปราการ",
    "province_name_en": "Samut Prakan",
    "region": "central"
  },
  {
    "province_id": "50",
    "province_name_th": "เชียงใหม่",
    "province_name_en": "Chiang Mai",
    "region": "north"
  }
]
```

## Regions (ภูมิภาค)

| Region Code | ชื่อภาค (ไทย) | ชื่อภาค (Eng) | จำนวนจังหวัด |
|-------------|--------------|--------------|-------------|
| `central` | ภาคกลาง | Central | 26 |
| `north` | ภาคเหนือ | Northern | 17 |
| `northeast` | ภาคตะวันออกเฉียงเหนือ | Northeastern (Isan) | 20 |
| `south` | ภาคใต้ | Southern | 14 |
| `east` | ภาคตะวันออก | Eastern | 7 |
| `west` | ภาคตะวันตก | Western | 5 |

## Usage in Forms

### Legal ภ.พ.09 Form

```html
<!-- Address fields with cascading dropdowns -->
<div class="grid grid-cols-2 gap-4">
  <div>
    <label for="province" class="block text-sm font-medium text-gray-700">จังหวัด *</label>
    <select id="province" name="province" required
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
      <option value="">-- เลือกจังหวัด --</option>
      <!-- Populated via JavaScript -->
    </select>
  </div>

  <div>
    <label for="district" class="block text-sm font-medium text-gray-700">อำเภอ/เขต *</label>
    <select id="district" name="district" required
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
      <option value="">-- เลือกอำเภอ/เขต --</option>
    </select>
  </div>

  <div>
    <label for="subdistrict" class="block text-sm font-medium text-gray-700">ตำบล/แขวง *</label>
    <select id="subdistrict" name="subdistrict" required
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
      <option value="">-- เลือกตำบล/แขวง --</option>
    </select>
  </div>

  <div>
    <label for="postal_code" class="block text-sm font-medium text-gray-700">รหัสไปรษณีย์ *</label>
    <input
      type="text"
      id="postal_code"
      name="postal_code"
      maxlength="5"
      pattern="\d{5}"
      required
      readonly
      class="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 shadow-sm focus:border-blue-500 focus:ring-blue-500">
  </div>
</div>

<script>
// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  initLocationDropdowns();
});
</script>
```

## Performance Considerations

### Caching

```python
# Cache province/district data (rarely changes)
from functools import lru_cache

@lru_cache(maxsize=1)
def get_provinces():
    """Cache provinces in memory (refresh on app restart)"""
    return bigquery_service.query_provinces()

@lru_cache(maxsize=77)
def get_districts(province_id: str):
    """Cache districts by province"""
    return bigquery_service.query_districts(province_id)
```

### Client-Side Caching

```javascript
// Cache in localStorage
const ProvinceCache = {
  get(key) {
    const data = localStorage.getItem(`location_${key}`);
    if (!data) return null;

    const parsed = JSON.parse(data);
    // Cache for 7 days
    if (Date.now() - parsed.timestamp > 7 * 24 * 60 * 60 * 1000) {
      return null;
    }

    return parsed.data;
  },

  set(key, data) {
    localStorage.setItem(`location_${key}`, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  }
};

// Use cache
async function getProvinces() {
  let provinces = ProvinceCache.get('provinces');

  if (!provinces) {
    const response = await API.get('/api/master-data/provinces');
    provinces = response.data;
    ProvinceCache.set('provinces', provinces);
  }

  return provinces;
}
```

## Validation

### Postal Code Validation

```python
def validate_postal_code(postal_code: str, province: str, district: str) -> bool:
    """Validate that postal code matches province and district"""

    result = bigquery_service.query(f"""
        SELECT COUNT(*) as count
        FROM retail_branches.subdistricts s
        JOIN retail_branches.districts d ON s.district_id = d.district_id
        WHERE s.postal_code = '{postal_code}'
          AND d.province_id = '{province}'
          AND d.district_id = '{district}'
    """)

    return result[0]['count'] > 0
```

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema
- [../frontend/javascript.md](../frontend/javascript.md) - Cascading dropdown implementation
- [../development/api-standards.md](../development/api-standards.md) - API conventions

# Development Guidelines

## Code Style

- **PEP 8 Compliance**: ใช้ PEP 8 style guide อย่างเคร่งครัด
- **Type Hints**: ใช้ type hints ทุก function และ method
- **Docstrings**: เขียน docstrings สำหรับ functions และ classes
- **Keep It Simple**: เน้นความเรียบง่าย ใช้ library น้อยที่สุด
- **Readability**: code ต้องอ่านง่าย ตั้งชื่อตัวแปรให้สื่อความหมาย

## Example Code Style

```python
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/branches")
async def get_branches_by_team(
    team: str = Query(..., description="ชื่อทีม (new_branch, legal, srd, scm)"),
    status: Optional[str] = Query(None, description="สถานะสาขา (active, opening, closed)")
) -> List[Dict[str, str]]:
    """
    ดึงข้อมูลสาขาตามทีมที่รับผิดชอบ

    Args:
        team: ชื่อทีม
        status: สถานะสาขา - optional

    Returns:
        List of branch dictionaries
    """
    # Implementation here
    pass
```

## Testing

- เขียน unit tests สำหรับ services
- เขียน integration tests สำหรับ API endpoints
- ใช้ pytest เป็น testing framework

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_services.py
```

## Security Considerations

- ใช้ Service Account แทนการใช้ API keys
- Validate input ทุกครั้งก่อนส่งไป BigQuery
- ตรวจสอบสิทธิ์การเข้าถึงตาม team
- ไม่เก็บ credentials ใน code หรือ git
- ใช้ environment variables สำหรับ sensitive data

## Git Workflow

### Branch Naming
- `feature/` - สำหรับ features ใหม่
- `bugfix/` - สำหรับแก้ bug
- `hotfix/` - สำหรับ urgent fixes

### Commit Messages
- ใช้ present tense ("Add feature" not "Added feature")
- เริ่มด้วย verb (Add, Update, Fix, Remove, etc.)
- ระบุเฉพาะเจาะจง

## Best Practices

1. **Keep Functions Small**: แต่ละ function ควรทำงานเดียว
2. **DRY Principle**: Don't Repeat Yourself
3. **Error Handling**: จัดการ errors อย่างเหมาะสม
4. **Logging**: ใช้ logging แทน print statements
5. **Code Review**: รอ code review ก่อน merge

## Related Documentation

- [setup.md](setup.md) - Local development setup
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture

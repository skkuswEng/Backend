사용자가 직접 정의한 class들 정리해놓는 리포지토리
ex.
'''python
class LatLngWithSum(BaseModel):  # BaseModel을 상속받아 정의
    latlng: Tuple[float, float]  # latlng 필드 타입을 Tuple로 변경
    sum: int
'''
from dao.base import BaseDao
from database.models.affiliate_applications.models import Affiliate_Applications

class Affiliate_ApplicationDAO(BaseDao):
    model = Affiliate_Applications
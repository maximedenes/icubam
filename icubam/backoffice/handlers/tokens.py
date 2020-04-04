import tornado.escape
import tornado.web

from icubam.backoffice.handlers import base
from icubam.backoffice.handlers import home
from icubam.db import store


class ListTokensHandler(base.AdminHandler):

  ROUTE = "/list_tokens"

  @tornado.web.authenticated
  async def get(self):
    clients = self.db.get_external_clients()
    data = [self.format_list_item(client.to_dict()) for client in clients]
    await self.render(
        "list.html", data=data, objtype='Acces Tokens',
        create_route=TokenHandler.ROUTE)


class TokenHandler(base.AdminHandler):

  ROUTE = "/token"

  @tornado.web.authenticated
  async def get(self):
    userid = self.get_query_argument('id', None)
    user = None
    if userid is not None:
      user = self.db.get_external_client(userid)

    user = user if user is not None else store.ExternalClient()
    await self.render("token.html", user=user, error="")

  @tornado.web.authenticated
  def post(self):
    fields = ['name', 'telephone', 'email']
    values = {k: self.get_body_argument(k, "") for k in fields}
    incoming_user = store.ExternalClient(**values)

    user = self.db.get_external_client_by_email(incoming_user.email)
    if user is None:
      self.db.add_external_client(self.user.user_id, incoming_user)
    else:
      c_id = user.external_client_id
      self.db.update_external_client(self.user.user_id, c_id, values)
    return self.redirect(ListTokensHandler.ROUTE)
